const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('canvas');
const canvasContext = canvasElement.getContext('2d');
const resultElement = document.getElementById('result');

// Create a popup element dynamically
const popup = document.createElement('div');
popup.id = 'popup';
popup.style.position = 'fixed';
popup.style.top = '50%';
popup.style.left = '50%';
popup.style.transform = 'translate(-50%, -50%)';
popup.style.background = 'rgba(0, 0, 0, 0.8)';
popup.style.color = '#fff';
popup.style.padding = '20px';
popup.style.borderRadius = '8px';
popup.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
popup.style.display = 'none';
document.body.appendChild(popup);

// Start the video stream from the user's camera
async function startVideo() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    videoElement.srcObject = stream;
    videoElement.setAttribute('playsinline', true); // required for iOS devices
    videoElement.play();
    requestAnimationFrame(scanQRCode);
}

let scanningPaused = false; // Flag to control scanning pause
// if there is no flag the function will keep on making ajax requests to server

async function scanQRCode() {
    if (scanningPaused) return; // Skip scanning if paused

    if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
        // Draw the video frame to the canvas
        canvasContext.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imageData = canvasContext.getImageData(0, 0, canvasElement.width, canvasElement.height);

        // Scan for QR code using jsQR
        const qrCode = jsQR(imageData.data, canvasElement.width, canvasElement.height);

        if (qrCode) {
            showPopup('Processing QR Code...');
            scanningPaused = true;

            // Pause scanning and send the QR code data to the server
            await sendQRCodeToServer(qrCode.data);

            // Resume scanning after 3 seconds
            setTimeout(() => {
                hidePopup();
                scanningPaused = false;
                requestAnimationFrame(scanQRCode);
            }, 3000);

            return; 
        }
    }

    // Continue scanning if not paused
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
                'X-CSRFToken': csrfToken, // Include CSRF token in the request header
            },
            body: JSON.stringify({ qr_code: qrData }), // Send the QR code data as JSON
        });

        const data = await response.json(); // Parse JSON response from the server
        if (data.success) {
            showPopup(`Success: ${data.message}`, 'success');
        } else {
            showPopup(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error sending QR code to server:', error);
        showPopup('An unexpected error occurred while sending the QR code.', 'error');
    }
}

// Function to show the popup
function showPopup(message, type = '') {
    popup.textContent = message;
    popup.style.display = 'block';

    // Apply different styles for success or error
    if (type === 'success') {
        popup.style.background = 'rgba(0, 128, 0, 0.8)';
    } else if (type === 'error') {
        popup.style.background = 'rgba(255, 0, 0, 0.8)';
    } else {
        popup.style.background = 'rgba(0, 0, 0, 0.8)';
    }
}

// Function to hide the popup
function hidePopup() {
    popup.style.display = 'none';
}

startVideo();
