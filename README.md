# Fingerprint 
Using R305 fingerprint module .
## Install neccessary packages.
```
pip install -r requirements.txt
```

## Fingerprint Functions.
* Enroll
* Remove
* Match
## Setting UART for Fingerprint using the 15_TX 16_RX pin
* Activate mini UART:

    Change to `enable_uart=1` flag in `config.txt` file

    ```
        vi /boot/config.txt
    ```


* Setting boaud rate :

    Remove `console=serial0,115200` or what is refers to serial0 devices

    ```
       vi /boot/cmdline.txt  
    ```
    



# GUI_Fingerprint
