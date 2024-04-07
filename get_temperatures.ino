void get_temperatures () {
  
  //Recupero il numero di sensori di temperatura e setto la sensibilitÃ  degli stessi.
  n_sonde = temp_sensors.getDeviceCount();
  Serial.print("Numero di sonde: ");
  Serial.println(n_sonde);
  Serial.println();
  temp_sensors.requestTemperatures();
  temp_sensors.setResolution(10);

  //Creo l'array di temperature misurate
  int i=0;
  while (i<n_sonde) {
    
    temperatures[i] = temp_sensors.getTempCByIndex(i);
    delay(100);
    temp[i] = temp_sensors.getTempCByIndex(i);
    delay(100);
    another_temp[i] = temp_sensors.getTempCByIndex(i);
    if ( temp[i]==temperatures[i] && temp[i]==another_temp[i] && temperatures[i] != -127.00 && temp[i] != -127.00 && another_temp[i] != -127.00 ) 
    {i++;}
  
  }
  
  
  // sorting dell'array, dalla temperatura piÃ¹ bassa alla piÃ¹ alta.
  for (int j = 0; j < n_sonde; j++) {
    for (int k = 0; k < n_sonde - 1; k++) {
      if (temperatures[k] > temperatures[k + 1]) {
        float tmp = temperatures[k + 1];
        temperatures[k + 1] = temperatures[k];
        temperatures[k] = tmp;
      }
    }
  }

  temp_cold1 = temperatures[0];
  temp_measured = temperatures[1];
  temp_hot = temperatures[2];
  /*
  for (int n = 0; n < n_sonde; n++) {
    Serial.print("Sorted Temperature ");
    Serial.println(n);
    Serial.println(temperatures[n]);
  }*
  
  cold_distance = temp_desired - temp_cold1;
  hot_distance  = temp_hot - temp_desired;
  distance = temp_desired - temp_measured; 
  distance_abs = abs(distance);
  
}
