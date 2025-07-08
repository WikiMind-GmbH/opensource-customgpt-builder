# React frontend
The frontend utilizes react with javascript. Using typescript in the future is the plan. 

## Development

### Installing new npm libraries (Docker workflow)
Everything is designed to run inside Docker containers.

When installing new npm libraries, start the frontend using its `docker-compose.dev.yaml` configuration:

```sh
docker-compose -f docker-compose.dev.yaml up
```

Then, open a shell inside the running frontend container:

```sh
docker-compose -f docker-compose.dev.yaml exec frontend /bin/sh
```

This gives you access to the container environment where you can safely run npm commands (e.g. `npm install some-package`).

### Generate client from openapi definition of backend
To generate a TypeScript client from the FastAPI backend:

1. If the FastAPI app is waiting for a debugger, start the debugger or set in the `.env` the following: `WAIT_FOR_DEBUGGER_IN_BACKEND=false`

2. Run the following Makefile command from the root of the full project:

   ```bash
   make generate-client-prod
   ```

3. As of now, we need to manually set the baseurl of the backend in the automatically generated frontend client. In the future, a makefile script might be used to do this.

In `frontend/src/client/core/OpenAPI.ts` set the `BASE`:
```py
export const OpenAPI: OpenAPIConfig = {
    BASE: 'http://localhost/api', #<-- set this value (use the value of env.BASE_URL + '/api')
    VERSION: '0.1.0',
    WITH_CREDENTIALS: false,
    CREDENTIALS: 'include',
    TOKEN: undefined,
    USERNAME: undefined,
    PASSWORD: undefined,
    HEADERS: undefined,
    ENCODE_PATH: undefined,
};
```

### Use it to call the endpoints

For each endpoint of fastapi there now is a function in one of the modules in `frontend/src/client/services`.
You can see that we have one service for each tag in fastapi and that for each endpoint, the name of the function in the frontend client is the operation-id we set in the fastapi endpoint.
`app.py`
```.py
@app.post(
    "/download-post/",
    tags=["images"], # <- YOU CAN FIND THE CLIENT FUNCTION IN THE IMAGESSERVICE MODULE
    summary="Downloads the images in original resolution, not the downscaled version of the served images endpoint",
    response_description="The images in original size",
    responses={
        200: {                               # mark it as binary in OpenAPI
            "content": {
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
            "description": "ZIP file containing images and post.txt",
        }
    },
    operation_id="downloadPostAsZip", # <- NAME OF THE GENERATED FUNCTION
)
async def dowload_original_sized_images(
    downloadInfos: PostDownload,
```

`frontend/src/client/services/ImagesService.ts` <- Module name is determined by the tag of the fastapi endpoint: `${fastapiTag}Service.ts`
```.ts
public static downloadPostAsZip( # <- SAME AS OPERATION_ID IN FASTAPI
        requestBody: PostDownload,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/download-post/',
            body: requestBody, 
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
```


The expected structure of the json body is encoded in the interfaces the client functions use, so you can easily see what body structure is expacted and get editor alrets if you pass incompatible bodys. Same endpoint and generated function as above:
```.py
 async def dowload_original_sized_images(
    downloadInfos: PostDownload, # <--
```

```.py
class PostDownload(BaseModel):
    requested_images: list[BasicImageIdentifiers]
    caption_text: str | None

class BasicImageIdentifiers(BaseModel):
    folderName: str
    fileName: str
    
```

This information is encoded in the generated client:
```.ts
public static downloadPostAsZip( // <- SAME AS OPERATION_ID IN FASTAPI
        requestBody: PostDownload, // <- Generated from the pydantic class the endpoint expects.
    ): 
```

```.ts
export type PostDownload = {
    requested_images: Array<BasicImageIdentifiers>;
    caption_text: (string | null);
};

export type BasicImageIdentifiers = {
    folderName: string;
    fileName: string;
};
```

You can then call it with
```.ts
import { ImagesService} from "../client"; // <- import the service module

const body: PostDownload = { // <- utilize the generated interface for type checking
      "requested_images": requestedImages,
      "caption_text": chatbotText
    };

const r = await ImagesService.downloadPostAsZip(body) <- call the endpoint>
```

However, watch out! We can not directly change the responseType of the function without modifying the generated client. As this would need to be done after each generation, it is better to utilize the interfaces and call the endpoint manually in these cases (is not necessary for most functions).

```.ts
const body: PostDownload = { // <- utilize the generated interface for type checking
      "requested_images": requestedImages,
      "caption_text": chatbotText
    };

const res = await axios.post('/api/download-post/', body, { 
    responseType: 'blob',
```
(Axios determines the domain for relative URLs like '/api/download-post/' based on the current origin of the page it's running on, that's why /api/download-post/ is enough)






This command uses `openapi-typescript-codegen` to generate a fully-typed client based on the OpenAPI spec served at `${FastapiBaseUrl}/openapi.json`.

Why this works:
The FastAPI backend automatically exposes an OpenAPI specification at:

```
${FastapiBaseUrl}/openapi.json
```

This specification is automatically generated using:

- **FastAPI decorators** (e.g. `@app.get`, `@app.post`) to define endpoints
- **Pydantic models** to define request/response schemas and validations
- **Route-level metadata** like `summary`, `description`, and `response_model` to enrich the documentation

This results in a complete, typed OpenAPI schema that accurately represents the backend API.

We use the `openapi-typescript-codegen` Node library to generate a strongly-typed TypeScript client from this spec. The generated client can be imported into the frontend to safely call backend endpoints with full type support.

The Makefile script `generate-client-prod` automates this process:

1. It checks that the backend container is healthy (i.e. that the OpenAPI spec is reachable).
2. It uses the OpenAPI spec to generate the client code.

This keeps the frontend client in sync with the backend API automatically.


