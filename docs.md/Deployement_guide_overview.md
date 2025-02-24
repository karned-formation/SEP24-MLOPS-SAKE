# Overview of deployed Docker Architecture (using Gateway)
![Gateway](../docs/sake.karned.bzh.png)
- Admin = Docker "**admin-frontend**"
- DVC = Docker "**admin-backend**"
- clean = Docker "**clean_text**"

Detailed documentation for the local deployement
- [Local deployement: secret management](Deployement_guide_Local_Secret_Management.md) 
- [Local deployement of the Prediction Dockers](Deployement_guide_Prediction_Pipeline_Local.md) 
- [Local deployement of the Training Dockers](Deployement_guide_Training_Pipeline_Local.md) 

Detailed documentation for the remote deployement
- User interface for Prediction is accessible at - [https://sake.karned.bzh](https://sake.karned.bzh/)
    - access with "toto" / "tutu"

- Admin interface for Training is accessible at - [https://admin.sake.karned.bzh](https://admin.sake.karned.bzh/)
- Admin interface for Grafana is accessible at - [https://grafana.sake.karned.bzh](https://grafana.sake.karned.bzh/d/cecfzm0ju4v0ga/mlops?orgId=1&from=now-15m&to=now&timezone=browser&refresh=10s)

- [Deployement Details (CI/CD)](../docs.md/Deployement_Details.md) 
