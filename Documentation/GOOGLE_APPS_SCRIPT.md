/\*\*

- IMS Email Service - Google Apps Script
-
- This script provides email sending functionality for the IMS system.
- Deploy as a web app and use the deployment URL in your Django settings.
-
- Setup Instructions:
- 1.  Go to https://script.google.com
- 2.  Create a new project
- 3.  Copy this entire code into the script editor
- 4.  Save the project with name "IMS Email Service"
- 5.  Click "Deploy" > "New Deployment"
- 6.  Select type "Web app"
- 7.  Set "Execute as" to your Google account
- 8.  Set "Who has access" to "Anyone"
- 9.  Click "Deploy"
- 10. Copy the deployment URL
- 11. Add to Django settings: APPS_SCRIPT_URL = "https://script.google.com/macros/d/{SCRIPT_ID}/usercontent"
      \*/

// Configuration
const CONFIG = {
// Gmail account that will send emails (should be your Google Workspace account)
FROM_EMAIL: Session.getActiveUser().getEmail(),

// CC emails for important notifications
CC_EMAILS: [
'jagruti@believersdestination.com',
'kunal@believersdestination.com',
'varun@believersdestination.com',
'chahat.gupta@believersdestination.com'
],

// Log sheet for tracking (optional)
ENABLE_LOGGING: true,
LOG_SHEET_NAME: 'Email Logs'
};

/\*\*

- Main handler for POST requests
  \*/
  function doPost(e) {
  try {
  const payload = JSON.parse(e.postData.contents);
      // Verify API key if configured
      if (payload.api_key && !validateApiKey(payload.api_key)) {
        return createResponse({
          success: false,
          error: 'Invalid API key'
        }, 401);
      }

      // Auto-detect email requests based on presence of 'to' and 'subject' fields
      if (payload.to && payload.subject) {
        return handleSendEmail(payload);
      } else if (payload.type === 'get_status') {
        return handleGetStatus();
      } else {
        return createResponse({
          success: false,
          error: 'Invalid request: missing required email fields (to, subject) or unknown request type'
        }, 400);
      }
  } catch (error) {
  logError('doPost', error);
  return createResponse({
  success: false,
  error: error.toString()
  }, 500);
  }
  }

/\*\*

- Handle email sending
  \*/
  function handleSendEmail(payload) {
  try {
  const {
  to,
  subject,
  htmlBody,
  textBody,
  cc = [],
  bcc = [],
  attachments = []
  } = payload;
      // Validate required fields
      if (!to || !subject) {
        return createResponse({
          success: false,
          error: 'Missing required fields: to, subject'
        }, 400);
      }

      // Combine CC emails
      const allCc = [...new Set([...cc, ...CONFIG.CC_EMAILS])];

      // Prepare email options
      const mailOptions = {
        to: to,
        subject: subject,
        htmlBody: htmlBody || textBody,
        textBody: textBody || htmlBody,
        cc: allCc.length > 0 ? allCc.join(', ') : undefined,
        bcc: bcc.length > 0 ? bcc.join(', ') : undefined,
        replyTo: CONFIG.FROM_EMAIL,
        noReply: false,
        from: CONFIG.FROM_EMAIL
      };

      // Remove undefined fields
      Object.keys(mailOptions).forEach(key =>
        mailOptions[key] === undefined && delete mailOptions[key]
      );

      // Send email
      GmailApp.sendEmail(
        mailOptions.to,
        mailOptions.subject,
        mailOptions.textBody,
        {
          htmlBody: mailOptions.htmlBody,
          cc: mailOptions.cc,
          bcc: mailOptions.bcc,
          replyTo: mailOptions.replyTo,
          from: mailOptions.from
        }
      );

      // Log the email
      if (CONFIG.ENABLE_LOGGING) {
        logEmail({
          to: to,
          cc: allCc.join(', '),
          subject: subject,
          status: 'sent',
          timestamp: new Date()
        });
      }

      return createResponse({
        success: true,
        message: 'Email sent successfully',
        recipient: to
      }, 200);

} catch (error) {
logError('handleSendEmail', error);
return createResponse({
success: false,
error: error.toString()
}, 500);
}
}

/\*\*

- Handle status check
  \*/
  function handleGetStatus() {
  return createResponse({
  success: true,
  status: 'active',
  timestamp: new Date(),
  message: 'IMS Email Service is running'
  }, 200);
  }

/\*\*

- Validate API key
  \*/
  function validateApiKey(apiKey) {
  // Store your API key in script properties for security
  // https://script.google.com/home/projects/{PROJECT_ID}/settings
  const scriptProperties = PropertiesService.getScriptProperties();
  const storedApiKey = scriptProperties.getProperty('IMS_API_KEY');

// If no API key is stored, accept any key (for development)
// Set a real key in script properties for production
if (!storedApiKey) {
return true;
}

return apiKey === storedApiKey;
}

/\*\*

- Log email to sheet
  \*/
  function logEmail(emailData) {
  try {
  const sheet = getOrCreateLogSheet();
  if (!sheet) return;
      const row = [
        emailData.timestamp,
        emailData.to,
        emailData.cc,
        emailData.subject,
        emailData.status
      ];

      sheet.appendRow(row);
  } catch (error) {
  logError('logEmail', error);
  }
  }

/\*\*

- Get or create log sheet
  \*/
  function getOrCreateLogSheet() {
  try {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.LOG_SHEET_NAME);
      if (!sheet) {
        sheet = ss.insertSheet(CONFIG.LOG_SHEET_NAME);
        sheet.appendRow(['Timestamp', 'To', 'CC', 'Subject', 'Status']);
      }

      return sheet;
  } catch (error) {
  logError('getOrCreateLogSheet', error);
  return null;
  }
  }

/\*\*

- Log errors
  \*/
  function logError(functionName, error) {
  const timestamp = new Date().toISOString();
  Logger.log(`[${timestamp}] Error in ${functionName}: ${error.toString()}`);

// Optionally send error notification
try {
GmailApp.sendEmail(
Session.getActiveUser().getEmail(),
`IMS Email Service Error - ${functionName}`,
error.toString(),
{
noReply: true
}
);
} catch (e) {
Logger.log(`Failed to send error notification: ${e}`);
}
}

/\*\*

- Create standardized response
  _/
  function createResponse(data, statusCode) {
  return ContentService
  .createTextOutput(JSON.stringify(data))
  .setMimeType(ContentService.MimeType.JSON)
  .setHeader('Access-Control-Allow-Origin', '_');
  }

/\*\*

- Test function to verify setup
  \*/
  function testEmailService() {
  try {
  const testData = {
  type: 'send_email',
  to: Session.getActiveUser().getEmail(),
  subject: 'IMS Email Service Test',
  htmlBody: '<h1>IMS Email Service is working!</h1><p>This is a test email.</p>',
  textBody: 'IMS Email Service is working! This is a test email.'
  };
      const response = handleSendEmail(testData);
      Logger.log('Test response: ' + JSON.stringify(JSON.parse(response.getContent())));

} catch (error) {
Logger.log('Test failed: ' + error.toString());
}
}

/\*\*

- Setup function to initialize script
  \*/
  function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('IMS Email Service')
  .addItem('Test Email Service', 'testEmailService')
  .addItem('View Email Logs', 'viewEmailLogs')
  .addToUi();
  }

/\*\*

- View email logs
  \*/
  function viewEmailLogs() {
  try {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.LOG_SHEET_NAME);
  if (sheet) {
  SpreadsheetApp.getUi().showModelessDialog(
  HtmlService.createHtmlOutput('<p>Email logs sheet is visible. Check the logs!</p>'),
  'Email Logs'
  );
  }
  } catch (error) {
  Logger.log('Error viewing logs: ' + error.toString());
  }
  }
