document.addEventListener('DOMContentLoaded', function () {

    const textInput = document.getElementById('textInput');
    const displayDiv = document.getElementById('displayDiv'); // Get the displayDiv element

    textInput.addEventListener('change', (event) => {
        const file = event.target.files[0];

        if (file.type === 'application/pdf') {
            const reader = new FileReader();

            reader.onload = (e) => {
                const pdfData = e.target.result;

                // Use PDF.js to extract text
                pdfjsLib.getDocument(pdfData).promise.then(function(pdf) {
                    const numPages = pdf.numPages;
                    let extractedText = '';

                    for (let i = 1; i <= numPages; i++) {
                        pdf.getPage(i).then(function(page) {
                            page.getTextContent().then(function(textContent) {
                                const pageText = textContent.items.map(item => item.str).join(' ');
                                extractedText += pageText + '\n';

                                // Display extracted text after all pages are processed
                                if (i === numPages) {
                                    displayDiv.textContent = extractedText; 
                                    sendMessage(extractedText); // Send the extracted text to the server
                                }
                            });
                        });
                    }
                });
            };

            reader.readAsArrayBuffer(file); // Read as ArrayBuffer for PDF.js
        } else {
            displayDiv.innerHTML = '<p>Please select a PDF file.</p>';
        }
    });

    function sendMessage(message) { 
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message }) // Send the extracted text
        })
        .then(response => response.json())
        .then(response => {
            const notification = document.querySelector('.notification');
            notification.innerHTML += '<p>' + "Please Wait, I am working on it..." + '</p>';
            notification.innerHTML += '<p><strong>Complexity:</strong> ' + response.epic_assessment.complexity + '</p>';
            notification.innerHTML += '<p><strong>Customer Collaboration:</strong> ' + response.epic_assessment.customer_collaboration + '</p>';
            notification.innerHTML += '<p><strong>Focus on Efficiency:</strong> ' + response.epic_assessment.focus_on_efficiency + '</p>';
            notification.innerHTML += '<p><strong>Focus on Quality:</strong> ' + response.message.epic_assessment.focus_on_quality + '</p>';
            notification.innerHTML += '<p><strong>Project Timeline:</strong> ' + response.epic_assessment.project_timeline + '</p>';
            notification.innerHTML += '<p><strong>Team Size and Structure:</strong> ' + response.epic_assessment.team_size_and_structure + '</p>';
            notification.innerHTML += '<p><strong>Time to Market:</strong> ' + response.epic_assessment.time_to_market + '</p>';
            notification.innerHTML += '<p><strong>Uncertainty:</strong> ' + response.epic_assessment.uncertainty + '</p>';
            notification.innerHTML += '<p><strong>Recommended Methodologies:</strong> ' + response.recommended_methodologies[0].methodology + ' ' + response.message.recommended_methodologies[1].methodology + ' ' + response.message.recommended_methodologies[2].methodology + '</p>';
            textInput.value = '';
            notification.scrollTop = notification.scrollHeight;

            if (response.js_code) {
                eval(response.js_code);
            }
            });
    }
});