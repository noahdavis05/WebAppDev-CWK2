const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('canvas');
const canvasContext = canvasElement.getContext('2d');
const resultElement = document.getElementById('result');

// Start the video stream from the user's camera
async function startVideo() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    videoElement.srcObject = stream;
    videoElement.setAttribute('playsinline', true); // required for iOS devices
    videoElement.play();
    requestAnimationFrame(scanQRCode);
}

// Function to scan QR Code in the video stream
async function scanQRCode() {
    if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
        // Draw the video frame to the canvas
        canvasContext.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imageData = canvasContext.getImageData(0, 0, canvasElement.width, canvasElement.height);

        // Scan for QR code using jsQR
        const qrCode = jsQR(imageData.data, canvasElement.width, canvasElement.height);

        if (qrCode) {
            resultElement.textContent = 'QR Code Detected: ' + qrCode.data;

            // Send the QR code data to the server via AJAX
            await sendQRCodeToServer(qrCode.data);
        } else {
            resultElement.textContent = 'No QR Code detected';
        }
    }
    // Continue scanning
    requestAnimationFrame(scanQRCode);
}

// Function to send QR code data to the server
async function sendQRCodeToServer(qrData) {
    console.log('Sending QR code to server:', JSON.stringify(qrData));

    // Get CSRF token from the meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    try {
        const response = await fetch('/scan-ticket', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,  // Include CSRF token in the request header
            },
            body: JSON.stringify({ qr_code: qrData }), // Send the QR code data as JSON
        });

        console.log('Response:', response);
        const data = await response.json(); // Assume the server responds with JSON
        if (data.success) {
            console.log('QR code processed successfully:', data.message);
        } else {
            console.error('Error processing QR code:', data.message);
        }
    } catch (error) {
        console.error('Error sending QR code to server:', error);
    }
}

// Start scanning when the page is ready
startVideo();
