# Frontend:

## Notes: Nodes
[Amazon SDK](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/index.html):

The frontend will contain all of the LEX interactions. This includes displaying chatbot functions and responses.

## Running for testing and development:

If this is a fresh pull, without any `node_modules`, go ahead and run:

```
npm install
```

This will go ahead and fetch all of the required node packages.

Then, once they have been installed, you can run and visualize the application by using:

```
npm start
```

This should go ahead and launch the developmenet server at [`http://localhost:3000`](http://localhost:3000) where all of the chatbot functionality should be linked.

## Deployment:

If the application is completed and it needs to be deployed, you can use:

```
npm run build
```

which will optimize and build the app under the `\build` folder.
