# otvl web site for blog.otvl.org

## Development setup

See otvl_web/doc/developer.md

Make otvl-web-lib and server directories from otvl_web repository accessibles:

    cd blog
    git clone https://github.com/t-beigbeder/otvl_web.git
    cd otvl_web
    git checkout ...

The directory otvl_web will be gitignored.

## Test the development

### API

Run python otvl_web/main

With the environment sample

    OTVL_WEB_CONFIG_PATH=path_to/otvl_blog/blog/data/config-dev.yml
    OTVL_WEB_HOST=0.0.0.0
    OTVL_WEB_INSECURE_CORS=1
    OTVL_WEB_LOGGING=DEBUG
    OTVL_WEB_PORT=9090
    OTVL_WEB_RELOAD=1
    OTVL_WEB_ROOT_PATH=/api/v2
    #OTVL_WEB_ASSETS_URL=http://otvl-dev-host:9090/api/v2/asset/

### Vue.js app

    cd blog/otvl_web/otvl-web-lib
    yarn install
    yarn build-lib
    cd ../../otvl-web-app
    yarn install
    yarn build
    yarn serve

## Test the stack

Now you can build and run the stack:

    # run a stack with traefik reverse proxy, apache web server and FastAPI API server
    docker-compose -f docker-compose-local.yml up -d --build
    # check log files
    docker-compose -f docker-compose-local.yml logs -f
    # update development
    # update the stack
    docker-compose -f docker-compose-local.yml up -d --build
    # clean up
    docker-compose -f docker-compose-local.yml down
    docker system prune

The application will be accessible at [https://otvl-dev-host:9443/](https://otvl-dev-host:9443/)

