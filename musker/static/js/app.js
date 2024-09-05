document.getElementById('loadDataBtn').addEventListener('click', function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/data/', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('dataContainer').innerHTML = xhr.responseText;
        }
    };
    xhr.send();
});
