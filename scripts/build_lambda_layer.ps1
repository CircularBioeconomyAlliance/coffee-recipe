# Build Lambda layer with pypdf for the lambda_function.py
# Run this script on Windows to create a Lambda layer zip file

$LAYER_NAME = "cba-lambda-dependencies"
$LAYER_DIR = "lambda_layer"

Write-Host "Building Lambda layer: $LAYER_NAME"

# Clean up previous build
if (Test-Path $LAYER_DIR) {
    Remove-Item -Recurse -Force $LAYER_DIR
}
New-Item -ItemType Directory -Path "$LAYER_DIR/python" -Force | Out-Null

# Install dependencies into the layer directory
# Note: For Lambda compatibility, you may need to build on Linux or use Docker
pip install --target "$LAYER_DIR/python" -r lambda_requirements.txt

# Create the zip file
Compress-Archive -Path "$LAYER_DIR/python" -DestinationPath "$LAYER_NAME.zip" -Force

Write-Host ""
Write-Host "Lambda layer created: $LAYER_NAME.zip"
Write-Host ""
Write-Host "IMPORTANT: For production, build the layer on Amazon Linux 2 or use Docker:"
Write-Host "  docker run --rm -v ${PWD}:/var/task public.ecr.aws/sam/build-python3.12 pip install -r lambda_requirements.txt -t lambda_layer/python"
Write-Host ""
Write-Host "To deploy this layer:"
Write-Host "  aws lambda publish-layer-version ``"
Write-Host "    --layer-name $LAYER_NAME ``"
Write-Host "    --zip-file fileb://$LAYER_NAME.zip ``"
Write-Host "    --compatible-runtimes python3.12 python3.11 ``"
Write-Host "    --compatible-architectures x86_64"
Write-Host ""
Write-Host "Then attach the layer to your Lambda function in the AWS Console or via CLI."
