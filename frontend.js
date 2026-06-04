 const VULNERABLE_API = 'https://sqlinjection-hackedversion-fixedversion-1.onrender.com';
 const SECURE_API = 'https://secure-sql-vulnerable.onrender.com';

        // Checking API connections
        async function checkAPIs() {
            try {
                const vulnCheck = fetch(`${VULNERABLE_API}/`).then(r => r.ok);
                const secCheck = fetch(`${SECURE_API}/`).then(r => r.ok);
                
                const [vulnOk, secOk] = await Promise.all([vulnCheck, secCheck]);
                
                const statusEl = document.getElementById('status');
                if (vulnOk && secOk) {
                    statusEl.className = 'status connected';
                    statusEl.innerHTML = '✅ Both APIs are running and connected!';
                } else {
                    statusEl.className = 'status disconnected';
                    statusEl.innerHTML = `⚠️ APIs not fully connected (Vulnerable: ${vulnOk ? '✓' : '✗'}, Secure: ${secOk ? '✓' : '✗'})`;
                }
            } catch (e) {
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('status').innerHTML = '❌ Unable to connect to APIs. Make sure both are running on ports 8000 and 8001';
            }
        }

        // Tab switching
        function switchTab(event, tabName) {
            event.preventDefault();
            
            const tabs = event.target.parentElement.querySelectorAll('.tab');
            tabs.forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');

            const prefix = tabName.split('-')[0];
            const type = tabName.split('-')[1];
            
            document.querySelectorAll(`.tab-content`).forEach(tc => {
                if (tc.id.startsWith(prefix)) {
                    tc.classList.remove('active');
                }
            });
            
            document.getElementById(tabName).classList.add('active');
        }

        // Exploiting Vulnerable Login
        async function exploitVulnerableLogin(event) {
            event.preventDefault();
            const username = document.getElementById('vuln-username').value;
            const password = document.getElementById('vuln-password').value;
            const resultEl = document.getElementById('vuln-login-result');
            const queryEl = document.getElementById('vuln-login-query');

            resultEl.innerHTML = '<div class="loading"></div> Sending attack...';
            resultEl.className = 'result-box pending';

            const generatedQuery = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
            queryEl.textContent = generatedQuery;
            queryEl.style.display = 'block';

            try {
                const response = await fetch(`${VULNERABLE_API}/login-vulnerable?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.success) {
                    resultEl.className = 'result-box success';
                    resultEl.innerHTML = `
                        <strong>✗ ATTACK SUCCESSFUL!</strong><br><br>
                        Logged in as: <strong>${data.user.username}</strong><br>
                        Email: ${data.user.email}<br><br>
                        <em>The SQL injection payload bypassed the password check!</em>
                    `;
                } else {
                    resultEl.className = 'result-box error';
                    resultEl.innerHTML = `<strong>Login Failed:</strong> ${data.message}`;
                }
            } catch (error) {
                resultEl.className = 'result-box error';
                resultEl.innerHTML = `<strong>Error:</strong> ${error.message}<br>Make sure the vulnerable API is running on port 8000`;
            }
        }

        // Exploiting Vulnerable Lookup
        async function exploitVulnerableLookup(event) {
            event.preventDefault();
            const userId = document.getElementById('vuln-userid').value;
            const resultEl = document.getElementById('vuln-lookup-result');
            const queryEl = document.getElementById('vuln-lookup-query');

            resultEl.innerHTML = '<div class="loading"></div> Sending attack...';
            resultEl.className = 'result-box pending';

            const generatedQuery = `SELECT * FROM users WHERE id = ${userId}`;
            queryEl.textContent = generatedQuery;
            queryEl.style.display = 'block';

            try {
                const response = await fetch(`${VULNERABLE_API}/get-user-vulnerable?user_id=${encodeURIComponent(userId)}`);
                const data = await response.json();

                if (data.success) {
                    resultEl.className = 'result-box success';
                    let html = '<strong>✗ DATA EXTRACTION SUCCESSFUL!</strong><br><br>';
                    html += `<strong>Returned ${data.users.length} users:</strong><br><br>`;
                    data.users.forEach(user => {
                        html += `👤 ${user.username} (${user.email})<br>`;
                    });
                    html += `<br><em>The OR 1=1 condition made the query return ALL users!</em>`;
                    resultEl.innerHTML = html;
                } else {
                    resultEl.className = 'result-box error';
                    resultEl.innerHTML = `<strong>Error:</strong> ${data.message}`;
                }
            } catch (error) {
                resultEl.className = 'result-box error';
                resultEl.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }

        // Exploiting Secure Login
        async function exploitSecureLogin(event) {
            event.preventDefault();
            const username = document.getElementById('sec-username').value;
            const password = document.getElementById('sec-password').value;
            const resultEl = document.getElementById('sec-login-result');
            const queryEl = document.getElementById('sec-login-query');

            resultEl.innerHTML = '<div class="loading"></div> Sending attack...';
            resultEl.className = 'result-box pending';

            queryEl.textContent = `SELECT * FROM users WHERE username = :username AND password = :password\n\nBindings: username="${username}", password="${password}"`;
            queryEl.style.display = 'block';

            try {
                const response = await fetch(`${SECURE_API}/login-secure?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.success) {
                    resultEl.className = 'result-box success';
                    resultEl.innerHTML = `
                        <strong>✓ Login Successful</strong><br><br>
                        Logged in as: <strong>${data.user.username}</strong><br>
                        Email: ${data.user.email}
                    `;
                } else {
                    resultEl.className = 'result-box error';
                    resultEl.innerHTML = `
                        <strong>✓ ATTACK PREVENTED!</strong><br><br>
                        <strong>Result:</strong> Invalid username or password<br><br>
                        <em>The parameterized query treated the entire string as a literal username value.</em><br>
                        <em>No user has username = "${username}"</em>
                    `;
                }
            } catch (error) {
                resultEl.className = 'result-box error';
                resultEl.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }

        // Exploiting Secure Lookup
        async function exploitSecureLookup(event) {
            event.preventDefault();
            const userId = document.getElementById('sec-userid').value;
            const resultEl = document.getElementById('sec-lookup-result');
            const queryEl = document.getElementById('sec-lookup-query');

            resultEl.innerHTML = '<div class="loading"></div> Sending attack...';
            resultEl.className = 'result-box pending';

            queryEl.textContent = `SELECT * FROM users WHERE id = :user_id\n\nBindings: user_id="${userId}"`;
            queryEl.style.display = 'block';

            try {
                const response = await fetch(`${SECURE_API}/get-user-orm?user_id=${encodeURIComponent(userId)}`);
                const data = await response.json();

                if (data.success && data.users.length > 0) {
                    resultEl.className = 'result-box success';
                    let html = '<strong>Returned user:</strong><br><br>';
                    data.users.forEach(user => {
                        html += `👤 ${user.username} (${user.email})<br>`;
                    });
                    resultEl.innerHTML = html;
                } else {
                    resultEl.className = 'result-box error';
                    resultEl.innerHTML = `
                        <strong>✓ ATTACK PREVENTED!</strong><br><br>
                        <strong>Result:</strong> No user found<br><br>
                        <em>FastAPI type validation rejected "${userId}" because it's not a valid integer.</em><br>
                        <em>Defense in depth: Type checking + Parameterized queries</em>
                    `;
                }
            } catch (error) {
                resultEl.className = 'result-box error';
                resultEl.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }

        // Clear functions
        function clearVulnLogin() {
            document.getElementById('vuln-login-result').innerHTML = '';
            document.getElementById('vuln-login-query').style.display = 'none';
        }

        function clearVulnLookup() {
            document.getElementById('vuln-lookup-result').innerHTML = '';
            document.getElementById('vuln-lookup-query').style.display = 'none';
        }

        function clearSecLogin() {
            document.getElementById('sec-login-result').innerHTML = '';
            document.getElementById('sec-login-query').style.display = 'none';
        }

        function clearSecLookup() {
            document.getElementById('sec-lookup-result').innerHTML = '';
            document.getElementById('sec-lookup-query').style.display = 'none';
        }

        // Checking the APIs on load
        checkAPIs();
        setInterval(checkAPIs, 5000);

        // Register User on BOTH APIs simultaneously
async function registerUser(event) {
    event.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const resultEl = document.getElementById('reg-result');

    resultEl.style.display = 'block';
    resultEl.className = 'result-box pending';
    resultEl.innerHTML = '<div class="loading"></div> Synchronizing across both API databases...';

    try {
        // Fire both fetch operations in parallel
        const vulnRegister = fetch(`${VULNERABLE_API}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        }).then(res => res.json());

        const secRegister = fetch(`${SECURE_API}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        }).then(res => res.json());

        // Wait for both cloud services to respond
        const [vulnData, secData] = await Promise.all([vulnRegister, secRegister]);

        if (vulnData.success && secData.success) {
            resultEl.className = 'result-box success';
            resultEl.innerHTML = `<strong>✓ Synchronization Successful!</strong> User <code>${username}</code> has been written to both the Vulnerable and Secure database files. Go ahead and test your payloads!`;
            
            // Clear inputs
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-password').value = '';
        } else {
            resultEl.className = 'result-box error';
            resultEl.innerHTML = `<strong>Sync Partial Failure:</strong><br>
                                   Vulnerable API: ${vulnData.message || '✓ Success'}<br>
                                   Secure API: ${secData.message || '✓ Success'}`;
        }
    } catch (error) {
        resultEl.className = 'result-box error';
        resultEl.innerHTML = `<strong>Network Error:</strong> Unable to communicate with one or both servers: ${error.message}`;
    }
}