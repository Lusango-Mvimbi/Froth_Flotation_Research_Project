# Clear Authentication Data Instructions

To clear stored authentication data from your browser:

## Method 1: Browser Console
1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Run these commands:

```javascript
// Clear all authentication data
localStorage.removeItem('auth_token');
localStorage.removeItem('current_user');
localStorage.removeItem('authToken');
localStorage.removeItem('userData');

// Verify it's cleared
console.log('Authentication data cleared');
console.log('Remaining localStorage items:', Object.keys(localStorage));
```

## Method 2: Browser Settings
1. Open browser settings
2. Go to Privacy & Security
3. Clear browsing data
4. Select "Local storage" and clear

## Method 3: Incognito/Private Mode
- Open the application in incognito/private mode for a fresh start

After clearing the data, restart the system and you should see the login page first.
