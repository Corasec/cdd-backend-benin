## Build & push the docker image

 After a docker login with the project account

```bash
cd src/
docker build . -t cosobenin/cdd-app:latest
docker push cosobenin/cdd-app:latest
```

