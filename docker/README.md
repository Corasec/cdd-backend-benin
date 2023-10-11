## Build & push the docker image

 After a docker login with the project account

```bash
cd src/
sudo docker build . -t cosobenin/cdd-app:latest
sudo docker push cosobenin/cdd-app:latest
```
