<html>
<head>

<link href="lightTheme.css" rel="stylesheet">

</head>
<body>
<h1> Using the SOC Simulator Web GUI</h1>

<h2> Configuring Settings</h2>

<p>Settings should be preconfigured for the lab environment, but you can check them in the settings tab.</p>

<p>Typical settings for the FortiPOC lab are as follows:</p>

<table>
  <tr>
    <th>Setting</th>
    <th>Description</th>
    <th>Typical Lab Value</th>
  </tr>
  <tr>
    <td>Server</td>
    <td>IP of FortiSOAR server</td>
    <td>10.0.1.6</td>
  </tr>
  <tr>
    <td>username</td>
    <td>FortiSOAR user</td>
    <td>csadmin</td>
  </tr>
  <tr>
    <td>password</td>
    <td>FortiSoar password</td>
    <td>changeme</td>
  </tr>
  <tr>
    <td>GUI Mode</td>
    <td>Local or Remote operation</td>
    <td>local</td>
  </tr>
</table>

<p>Other settings should not affect the lab. Settings may vary between labs, check with your instructor if unsure.</p>

<h2>System Errors</h2>

Errors running steps are logged to a file called simulator_error.log in the base directory (usually /var/www/html/soc_simulator/). Check this file if the steps do not return after a few minutes.

If the application cannot write here, check permissions on the directory.

<h2>GUI Overview</h2>

<img src="guiOverview.png" width="1500">

<h3>GUI Theme</h3>

The GUI uses a dark theme. If you need to switch to a light theme for accessibility reasons then contact your instructor.

<h2>Selecting and Running a Preconfigured Scenario</h2>

<p>The menus are created dynamically by the GUI based on avaialble scenarios. The avaialble categories and scenarios may be different to those shown in the screenshot.</p>

<h3>Step 1 - Select a Scenario Category</h3>

<p>Choose a secnario category from the avaialble categories in the top menu [1].

<h3>Step 2 - Select an Available Scenario</h3>

<p>Choose one of the scenarios from the scenario menu on the left [2].

<h3>Step 3 - Review the Scenario Details and Requirements</h3>

<p>Read the scenario information, and check that the required dependencies have been met. These typically include FortiSOAR connector installation and configuration. 

<p>Ensure dependeices are configured before running the scenario, otherwise the scenario will fail.

<p>Review the step information in the step table on the right of the page.

<h3b>Step 4 - Run the Steps</h3>

<p>Use the "Execute Step" buttons [4] to run each step as required. The step output is displayed in the box underneath [5]. <i><b>Click the button once and wait - it can take a little time for the step to complete and display any output.</b></i>

<h3>Restarting a scenario</h3>

<p>Refresh the page and navigate back to the scenario to start over. 

<h2> Customizing a Scenario</h2>

<p>Scenarios can be customized. This feature can be used to mode the scenario more relevent to a specific region by changing IP or Geo data, or to investigate the effect of changing alert attributes such as severity.

<p>The system only supports a single custom scenario. Selecting a scenario to customze will overwrite any previous custom scenario, which will be erased and cannot be restored.

<p>This is a Beta feature:

<ul>
  <li>It is not possible to edit all types of scenario steps. Some steps containing certain data such as HTML formatted email are not displayed correctly by the editor and cannot be edited
  <li>The "Insert Step" and "Delete Step" features are not yet implemented
</ul>

<h3>Step 1 - Select a Scenario to Customize</h3>

<p>Select one of the existing scenarios and click the "Customize (Overwrite existing custom scenario)" button [6]. Confirm or cancel in the next screen. The selected scenario is copied to the "my scenarios" tab.

<h3>Step 2 - Review the Scenario Data and Edit</h3>

<p>The raw data for each step is displayed in the GUI. Choose a step to edit and click the "Edit Step" button to load the step into the editor. The "Delete Step" and "Insert Step" buttons are not currently impelemented.</p>

<img src="viewStep.png" width="1500">

<p>The step is loaded into the editor. The attribute name is shown in the first column, the current value in the second column. The third column can be modified to the new value as required. Once all modifications have been made, scroll to the bottom and click "Save"</p>

<img src="editStep.png" width="1500">

<p>The step data is updated with the new value. Repeat the process for another step in the scenario if required.</p>

<h3>Step 3 - Replay the Custom Scenario</h3>

Replay the custom scenario by selecting "MyScenario" from the left menu. The MyScenario page is used in the same way as the regular scenario replay pages.

<ul>
  <li>The scenario information table is copied from the original scenario. It is not currently possible to edit this
  <li>It is not currently possible to upload a diagram to MyScenario
</ul>

<i><b>MyScenario will be overwritten if another scenario is selected for customization</b></i>

