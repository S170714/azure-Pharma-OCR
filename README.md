# azure-Pharma-OCR
This Project is About Classification  of Pharmaceutical  tablets using Azure Cognitive Service Custom Vision,Implementing the web application in Asp.net

Create an image classification project with the Custom Vision client library or REST API

Get started with the Custom Vision client library for .NET. Follow these steps to install the package and try out the example code for building an image classification model. You'll create a project, add tags, train the project, and use the project's prediction endpoint URL to programmatically test it. Use this example as a template for building your own image recognition app.

Use the Custom Vision client library for .NET to:

Create a new Custom Vision project
Add tags to the project
Upload and tag images
Train the project
Publish the current iteration
Test the prediction endpoint

Prerequisites
Azure subscription - Create one for free
The Visual Studio IDE or current version of .NET Core.
Once you have your Azure subscription, create a Custom Vision resource in the Azure portal to create a training and prediction resource and get your keys and endpoint. Wait for it to deploy and click the Go to resource button.
You will need the key and endpoint from the resources you create to connect your application to Custom Vision. You'll paste your key and endpoint into the code below later in the quickstart.
You can use the free pricing tier (F0) to try the service, and upgrade later to a paid tier for production.

Setting up
Create a new C# application
Visual Studio IDE
CLI
Using Visual Studio, create a new .NET Core application.

Install the client library
Once you've created a new project, install the client library by right-clicking on the project solution in the Solution Explorer and selecting Manage NuGet Packages. In the package manager that opens select Browse, check Include prerelease, and search for Microsoft.Azure.CognitiveServices.Vision.CustomVision.Training and Microsoft.Azure.CognitiveServices.Vision.CustomVision.Prediction. Select the latest version and then Install.

From the project directory, open the program.cs file and add the following using directives:

C#

Copy
using Microsoft.Azure.CognitiveServices.Vision.CustomVision.Prediction;
using Microsoft.Azure.CognitiveServices.Vision.CustomVision.Training;
using Microsoft.Azure.CognitiveServices.Vision.CustomVision.Training.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
In the application's Main method, create variables for your resource's key and endpoint. You'll also declare some basic objects to be used later.

C#

Copy
// You can obtain these values from the Keys and Endpoint page for your Custom Vision resource in the Azure Portal.
private static string trainingEndpoint = "PASTE_YOUR_CUSTOM_VISION_TRAINING_ENDPOINT_HERE";
private static string trainingKey = "PASTE_YOUR_CUSTOM_VISION_TRAINING_SUBSCRIPTION_KEY_HERE";
// You can obtain these values from the Keys and Endpoint page for your Custom Vision Prediction resource in the Azure Portal.
private static string predictionEndpoint = "PASTE_YOUR_CUSTOM_VISION_PREDICTION_ENDPOINT_HERE";
private static string predictionKey = "PASTE_YOUR_CUSTOM_VISION_PREDICTION_SUBSCRIPTION_KEY_HERE";
// You can obtain this value from the Properties page for your Custom Vision Prediction resource in the Azure Portal. See the "Resource ID" field. This typically has a value such as:
// /subscriptions/<your subscription ID>/resourceGroups/<your resource group>/providers/Microsoft.CognitiveServices/accounts/<your Custom Vision prediction resource name>
private static string predictionResourceId = "PASTE_YOUR_CUSTOM_VISION_PREDICTION_RESOURCE_ID_HERE";

private static List<string> hemlockImages;
private static List<string> japaneseCherryImages;
private static Tag hemlockTag;
private static Tag japaneseCherryTag;
private static Iteration iteration;
private static string publishedModelName = "treeClassModel";
private static MemoryStream testImage;
 Important

Go to the Azure portal. If the Custom Vision resources you created in the Prerequisites section deployed successfully, click the Go to Resource button under Next Steps. You can find your keys and endpoint in the resources' key and endpoint pages. You'll need to get the keys for both your training and prediction resources, along with the API endpoint for your training resource.

You can find the prediction resource ID on the resource's Properties tab in the Azure portal, listed as Resource ID.

 Important

Remember to remove the keys from your code when you're done, and never post them publicly. For production, use a secure way of storing and accessing your credentials like Azure Key Vault. See the Cognitive Services security article for more information.

In the application's Main method, add calls for the methods used in this quickstart. You will implement these later.

C#

Copy
CustomVisionTrainingClient trainingApi = AuthenticateTraining(trainingEndpoint, trainingKey);
CustomVisionPredictionClient predictionApi = AuthenticatePrediction(predictionEndpoint, predictionKey);

Project project = CreateProject(trainingApi);
AddTags(trainingApi, project);
UploadImages(trainingApi, project);
TrainProject(trainingApi, project);
PublishIteration(trainingApi, project);
TestIteration(predictionApi, project);
DeleteProject(trainingApi, project);

Authenticate the client
In a new method, instantiate training and prediction clients using your endpoint and keys.

C#

Copy
private static CustomVisionTrainingClient AuthenticateTraining(string endpoint, string trainingKey)
{
    // Create the Api, passing in the training key
    CustomVisionTrainingClient trainingApi = new CustomVisionTrainingClient(new Microsoft.Azure.CognitiveServices.Vision.CustomVision.Training.ApiKeyServiceClientCredentials(trainingKey))
    {
        Endpoint = endpoint
    };
    return trainingApi;
}
private static CustomVisionPredictionClient AuthenticatePrediction(string endpoint, string predictionKey)
{
    // Create a prediction endpoint, passing in the obtained prediction key
    CustomVisionPredictionClient predictionApi = new CustomVisionPredictionClient(new Microsoft.Azure.CognitiveServices.Vision.CustomVision.Prediction.ApiKeyServiceClientCredentials(predictionKey))
    {
        Endpoint = endpoint
    };
    return predictionApi;
}
Create a new Custom Vision project
This next bit of code creates an image classification project. The created project will show up on the Custom Vision website. See the CreateProject method to specify other options when you create your project (explained in the Build a classifier web portal guide).

C#

Copy
private static Project CreateProject(CustomVisionTrainingClient trainingApi)
{
    // Create a new project
    Console.WriteLine("Creating new project:");
    return trainingApi.CreateProject("My New Project");
}
Add tags to the project
This method defines the tags that you will train the model on.

C#

Copy
private static void AddTags(CustomVisionTrainingClient trainingApi, Project project)
{
    // Make two tags in the new project
    hemlockTag = trainingApi.CreateTag(project.Id, "Hemlock");
    japaneseCherryTag = trainingApi.CreateTag(project.Id, "Japanese Cherry");
}
Upload and tag images
First, download the sample images for this project. Save the contents of the sample Images folder to your local device.

Then define a helper method to upload the images in this directory. You may need to edit the GetFiles argument to point to the location where your images are saved.

C#

Copy
private static void LoadImagesFromDisk()
{
    // this loads the images to be uploaded from disk into memory
    hemlockImages = Directory.GetFiles(Path.Combine("Images", "Hemlock")).ToList();
    japaneseCherryImages = Directory.GetFiles(Path.Combine("Images", "Japanese_Cherry")).ToList();
    testImage = new MemoryStream(File.ReadAllBytes(Path.Combine("Images", "Test", "test_image.jpg")));
}
Next, define a method to upload the images, applying tags according to their folder location (the images are already sorted). You can upload and tag images iteratively, or in a batch (up to 64 per batch). This code snippet contains examples of both.

C#

Copy
private static void UploadImages(CustomVisionTrainingClient trainingApi, Project project)
{
    // Add some images to the tags
    Console.WriteLine("\tUploading images");
    LoadImagesFromDisk();

    // Images can be uploaded one at a time
    foreach (var image in hemlockImages)
    {
        using (var stream = new MemoryStream(File.ReadAllBytes(image)))
        {
            trainingApi.CreateImagesFromData(project.Id, stream, new List<Guid>() { hemlockTag.Id });
        }
    }

    // Or uploaded in a single batch 
    var imageFiles = japaneseCherryImages.Select(img => new ImageFileCreateEntry(Path.GetFileName(img), File.ReadAllBytes(img))).ToList();
    trainingApi.CreateImagesFromFiles(project.Id, new ImageFileCreateBatch(imageFiles, new List<Guid>() { japaneseCherryTag.Id }));

}
Train the project
This method creates the first training iteration in the project. It queries the service until training is completed.

C#

Copy
private static void TrainProject(CustomVisionTrainingClient trainingApi, Project project)
{
    // Now there are images with tags start training the project
    Console.WriteLine("\tTraining");
    iteration = trainingApi.TrainProject(project.Id);

    // The returned iteration will be in progress, and can be queried periodically to see when it has completed
    while (iteration.Status == "Training")
    {
        Console.WriteLine("Waiting 10 seconds for training to complete...");
        Thread.Sleep(10000);

        // Re-query the iteration to get it's updated status
        iteration = trainingApi.GetIteration(project.Id, iteration.Id);
    }
}
 Tip

Train with selected tags

You can optionally train on only a subset of your applied tags. You may want to do this if you haven't applied enough of certain tags yet, but you do have enough of others. In the TrainProject call, use the trainingParameters parameter. Construct a TrainingParameters and set its SelectedTags property to a list of IDs of the tags you want to use. The model will train to only recognize the tags on that list.

Publish the current iteration
This method makes the current iteration of the model available for querying. You can use the model name as a reference to send prediction requests. You need to enter your own value for predictionResourceId. You can find the prediction resource ID on the resource's Properties tab in the Azure portal, listed as Resource ID.

C#

Copy
private static void PublishIteration(CustomVisionTrainingClient trainingApi, Project project)
{
    trainingApi.PublishIteration(project.Id, iteration.Id, publishedModelName, predictionResourceId);
    Console.WriteLine("Done!\n");

    // Now there is a trained endpoint, it can be used to make a prediction
}
Test the prediction endpoint
This part of the script loads the test image, queries the model endpoint, and outputs prediction data to the console.

C#

Copy
private static void TestIteration(CustomVisionPredictionClient predictionApi, Project project)
{

    // Make a prediction against the new project
    Console.WriteLine("Making a prediction:");
    var result = predictionApi.ClassifyImage(project.Id, publishedModelName, testImage);

    // Loop over each prediction and write out the results
    foreach (var c in result.Predictions)
    {
        Console.WriteLine($"\t{c.TagName}: {c.Probability:P1}");
    }
}
Run the application
Visual Studio IDE
CLI
Run the application by clicking the Debug button at the top of the IDE window.

As the application runs, it should open a console window and write the following output:

Console

Copy
Creating new project:
        Uploading images
        Training
Done!

Making a prediction:
        Hemlock: 95.0%
        Japanese Cherry: 0.0%
You can then verify that the test image (found in Images/Test/) is tagged appropriately. Press any key to exit the application. You can also go back to the Custom Vision website and see the current state of your newly created project.
Clean up resources
If you wish to implement your own image classification project (or try an object detection project instead), you may want to delete the tree identification project from this example. A free subscription allows for two Custom Vision projects.

On the Custom Vision website, navigate to Projects and select the trash can under My New Project.


![Screenshot (29)](https://user-images.githubusercontent.com/109462415/222712496-de58b9ae-23a6-46d1-9474-dc0d758640e9.png)
![Screenshot (30)](https://user-images.githubusercontent.com/109462415/222712509-5df2c40c-f5c3-4394-be96-e4a9e2b51c8a.png)
![Screenshot (31)](https://user-images.githubusercontent.com/109462415/222712512-20ed1bca-fb1b-45d4-9633-eb2cf59fde92.png)


Next steps
Now you've done every step of the image classification process in code. This sample executes a single training iteration, but often you'll need to train and test your model multiple times in order to make it more accurate.


What is Custom Vision?
The source code for this sample can be found on GitHub
SDK reference documentation
