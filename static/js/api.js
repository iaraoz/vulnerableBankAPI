
function storeToken(token) {
    localStorage.setItem('auth_token', token);
}


function getToken() {
    return localStorage.getItem('auth_token');
}


function clearToken() {
    localStorage.removeItem('auth_token');
}


function getUserId() {
    return localStorage.getItem('user_id');
}


function storeUserId(userId) {
    localStorage.setItem('user_id', userId);
}


async function login(username, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            storeToken(data.token);
            storeUserId(data.user_id);
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}


async function getUserProfile(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Get profile error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}


async function getUserAccounts(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/accounts`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Get accounts error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}

// Get account details
async function getAccountDetails(accountId) {
    try {
        const response = await fetch(`/api/accounts/${accountId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Get account details error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}

// Get account transactions
async function getAccountTransactions(accountId) {
    try {
        const response = await fetch(`/api/transactions/${accountId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Get transactions error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}

// Transfer money
async function transferMoney(fromAccount, toAccount, amount, description) {
    try {
        const response = await fetch('/api/transfer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                from_account: fromAccount,
                to_account: toAccount,
                amount,
                description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Transfer error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}

// Search transactions
async function searchTransactions(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Search error:', error);
        return { success: false, error: 'Network error or server unavailable' };
    }
}

// Check if the user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Logout function
function logout() {
    clearToken();
    localStorage.removeItem('user_id');
    window.location.href = '/login';
}
