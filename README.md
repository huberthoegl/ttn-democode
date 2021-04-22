# ttn-democode
The Things Network Democode

Hubert Högl, <Hubert.Hoegl@hs-augsburg.de>

* `co2ampel_plot.py` - Read SCD30 sensor data from storage integration and 
  display the last 7 days in three subplots (co2, temperature, humidity).

  Set environment variable ACCESSKEY to the access key of application
  `fr_co2ampel_hft`:

  https://console.thethingsnetwork.org/applications/fr_co2ampel_hft


  ```
  $ export ACCESSKEY=...
  ```

* `co2ampel_client.py` - Read sensor values with MQTT callback and store them
  in a InfluxDB.



