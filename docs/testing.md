# Testing

The design report proposes tests for authentication, control operations and responsiveness.
The *Walkthrough* column links these tests to related scenes in the
[silent walkthrough video](../assets/video/hmi-walkthrough.mp4), not to recorded pass results.
No completed test log, measured response times or independent plant commissioning evidence
was supplied. All expected results below remain acceptance criteria to verify in TIA Portal.

| ID | Test | Steps | Expected result | Walkthrough |
| --- | --- | --- | --- | --- |
| TC-01 | User login | open the login screen, enter user name and password, press *Login* | access granted for valid credentials, error otherwise | omitted for privacy |
| TC-02 | Toggle manual / auto mode | open the control mode selection, press the toggle | mode switches and the display updates | 01:41 |
| TC-03 | Control valves / motors in manual mode | select a valve or motor, press *ON* / *OFF* | the selected component responds | 01:14 |
| TC-04 | View I/O status | open the I/O status screen | real-time values are displayed | 02:18 |
| TC-05 | Monitor tank levels | open the monitoring screen, watch the tank animations | correct levels, animations update | 01:41 |
| TC-06 | View alarm status | trigger an alarm condition, open the alarm screen | alarm indication appears with the correct status | 02:43 |
| TC-07 | Set operational parameters | open the parameters, enter new values (e.g. flow rate), confirm | new settings are applied | 01:58 |
| TC-08 | Create / edit recipe | open recipe management, create or edit a recipe, save | recipe is saved and listed | 00:22 |
| TC-09 | Acknowledge and reset alarms | open the alarm screen, press *Acknowledge*, then *Reset* | alarm clears after reset | 02:43 (screen only) |
| TC-11 | Save and load recipe | save a new recipe, load it again | the recipe loads with the correct parameters | 00:55 |
| TC-12 | Toggle language (ENG / DEU) | switch the language | all UI texts change to the selected language | 02:26 |
| TC-13 | Navigate between screens | use the navigation buttons (Main, Recipe, Parameter, ...) | screens change without lag or errors | throughout |
| TC-14 | Handle batch data | enter batch details (ID, size, timestamp), check them | batch data is stored and displayed | 01:10 (display only) |
| TC-17 | Alarm notification visibility | trigger an alarm, check the indicator | the alarm notification is clearly visible | 02:38 |
| TC-18 | System responsiveness | perform several actions quickly (navigate, enter values) | no freezing or unresponsive behaviour | - |
| TC-19 | Incorrect input handling | enter invalid data (e.g. letters in numeric fields) | input is rejected with a message | - |

Test IDs follow the original plan, which skips TC-10, TC-15 and TC-16.
In particular, the video does not establish invalid-login handling, alarm acknowledgment,
batch persistence, responsiveness under load or invalid-input rejection.

## Test environments

| Environment | Purpose |
| --- | --- |
| WinCC Runtime Advanced simulation (TP700 Comfort device frame) | recorded demonstrations of screens, pop-ups, recipes, languages and user management |
| SIMATIC TP700 Comfort panel | recorded touch operation on real hardware, shown in the separate clip below |

![Real TP700 Comfort panel](../assets/gifs/hardware.gif)

## Automated checks in this repository

The engineering data is not only documented but also verified: the [CI workflow](../.github/workflows/ci.yml)
parses the TIA Portal printout on every push and checks the extracted tables (screens, tags, I/O, alarms,
recipes, user groups) against [`data/`](../data), and checks that every local link and image in the
documentation resolves. Run the same checks locally with `pytest`.

These checks validate the documentation package, not PLC control logic, safety interlocks or
HMI runtime behavior. CI results are available only after the workflow runs on GitHub.
