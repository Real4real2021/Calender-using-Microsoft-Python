document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        dateClick: function(info) {
            alert('Clicked on: ' + info.dateStr);
        }
    });
    calendar.render();

    // --- Access tasks passed from the server ---
    const tasks = JSON.parse('{{ tasks | tojson | safe }}'); // Assuming tasks are passed from Flask

    if (tasks) {
        tasks.forEach(task => {
            calendar.addEvent({
                title: task.title,
                start: task.start 
            });
        });
    } 
});
