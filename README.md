# HA-Custom-Component

Intégrations Home Assistant personnalisées (usage privé, non HACS-officiel).

## linge_suivi

Suit la durée de chaque cycle (lave-linge / sèche-linge) à partir d'un
`binary_sensor` "en marche" existant (seuil de puissance + délai de
confirmation), et expose un capteur `Dernière durée de cycle` rattaché au
device de l'appareil.

- Persistance via le `Store` natif Home Assistant (survit aux redémarrages,
  indépendante de la purge du recorder).
- Historique des derniers cycles (jusqu'à 200) dans les attributs du capteur.
- Configuration via un domaine YAML `linge_suivi:` (dict clé = nom de
  l'appareil), importé automatiquement en config entry au démarrage — permet
  le rattachement au device HA existant (impossible via une simple plateforme
  YAML `sensor: platform:`).

### Configuration

```yaml
linge_suivi:
  lave_linge:
    source: binary_sensor.lave_linge_en_marche
    name: "Lave-linge"
    device_id: "<device_id HA existant>"
```

- `source` (obligatoire) : entity_id d'un binary_sensor "en marche".
- `name` (optionnel) : nom affiché.
- `device_id` (optionnel) : device HA existant auquel rattacher le capteur.
