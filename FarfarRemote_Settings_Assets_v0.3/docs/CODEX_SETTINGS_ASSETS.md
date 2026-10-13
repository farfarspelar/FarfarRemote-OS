# Codex – Settings-uppdatering

Integrera tillhörande Settings-grafikpaket i befintligt FarfarRemote-repo utan att skapa ett parallellt projekt. Låt huvudvyns utseende och funktion vara intakta. Gör Settings till en mörk, konsekvent vy med samma midnattsblå och cyan accent som fjärrkontrollen. Huvudmålet är bättre läsbarhet och touchvänlighet, inte så många effekter som möjligt.

Använd individuella PNG-ikoner och de transparenta knapp-/fältbakgrunderna. Text, lösenord, port, IP-adress, fel och status ska renderas dynamiskt i Android, inte bakas in i bilder. Gör konkreta XML-/Java-vyer för input, toggles, Portrait/Landscape/Auto, Test Connection, Save, Wi-Fi Settings, System Information. Stöd API 19, bibehåll HOME-intent, autentisering och inställningsmigration från 0.1/0.2.

Längst ner i Settings/About: skapa en subtil valfri Buy Me a Coffee-knapp med `button_coffee_discreet.png` och `ic_coffee.png`. Den ska bara visas när ägaren konfigurerat en riktig Buy Me a Coffee-URL. Öppna den externt via säker ACTION_VIEW. Inga antagna konton, inga betalningar i appen och inga popups.

Kontrollera alpha, bildstorlekar, app-minne, navigering, skärmläge, ADB-installation och offline Settings. Bygg APK och dokumentera verkligt testade funktioner. Rör inte debloat, bootloader eller systempartitioner.
