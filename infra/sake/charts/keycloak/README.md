# Helm de déploiement Keycloak

**Création du secret**
```sh
kubectl create secret generic keycloak-secret \
  --namespace sake \
  --from-literal=KEYCLOAK_URL=<keycloak-url> \
  --from-literal=CLIENT_ID=<client-id> \
  --from-literal=CLIENT_SECRET=<client-secret>
```

**Déploiement**
```sh
 helm install keycloak ./keycloak -f keycloak/values.yaml
```

**Suppression**
```sh
helm uninstall keycloak -n sake
```

