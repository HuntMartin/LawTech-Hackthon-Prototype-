document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    
    loginForm.addEventListener('submit', async (event) => {
        // Prevent the default form submission
        event.preventDefault();
        
        // You can add your authentication logic here
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try{
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: username, password: password})
            });
            if(response.ok){
                alert('Login successful!');
                window.location.href = '/';
            } else{
                alert('Login failed!');
            }
        } catch(error){
            alert('Login failed!');
        }
    });
});