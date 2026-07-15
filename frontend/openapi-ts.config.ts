import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "http://backend:5173/openapi.json",
  output: "src/client",
  plugins: [
    "@hey-api/typescript",
    {
      name: "@hey-api/client-axios",
      throwOnError: true,
    },
    {
      name: "@hey-api/sdk",
      client: "@hey-api/client-axios",
      paramsStructure: "grouped",
    },
  ],
});
