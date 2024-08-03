# Weather Notifier

This project fetches weather forecast data and sends notifications to your phone using Pushover. Follow the steps below to set up and run the script.

## Prerequisites

- Python 3.x
- Pushover app installed on your phone (iOS or Android)
- GitHub account (optional, for version control and hosting)

## Setup Guide

### 1. Install the Pushover App

1. Download and install the Pushover app on your phone:
   - [Pushover for iOS](https://apps.apple.com/app/id506088175)
   - [Pushover for Android](https://play.google.com/store/apps/details?id=net.superblock.pushover)

2. Sign up for a Pushover account on the app or [Pushover website](https://pushover.net/).

### 2. Get Your Pushover User Key and Create an Application

1. Log in to your Pushover account on the [Pushover website](https://pushover.net/).
2. Your User Key can be found on the [dashboard](https://pushover.net/dashboard).
3. Create a new application on the [Applications & Plugins](https://pushover.net/apps/build) page to get an API token.

### 3. Clone the Repository and Navigate to the Project Directory

```bash
git clone https://github.com/yourusername/weathernotifier.git
cd weathernotifier
```
### 4. Install Required Python Libraries
```
pip install requests
