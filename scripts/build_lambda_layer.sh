#!/bin/bash
# Build Lambda layer with pypdf for the lambda_function.py
# Run this script to create a Lambda layer zip file

set -e

LAYER_NAME="cba-lambda-dependencies"
LAYER_DIR="lambda_layer"
PYTHON_VERSION="python3.12"

echo "Building Lambda layer: $LAYER_NAME"

# Clean up previous build
rm -rf $LAYER_DIR
mkdir -p $LAYER_DIR/python

# Install dependencies into the layer directory
pip install --target $LAYER_DIR/python -r lambda_requirements.txt --platform manylinux2014_x86_64 --only-binary=:all:

# Create the zip file
cd $LAYER_DIR
zip -r ../${LAYER_NAME}.zip python/
cd ..

echo "Lambda layer created: ${LAYER_NAME}.zip"
echo ""
echo "To deploy this layer:"
echo "  aws lambda publish-layer-version \\"
echo "    --layer-name $LAYER_NAME \\"
echo "    --zip-file fileb://${LAYER_NAME}.zip \\"
echo "    --compatible-runtimes python3.12 python3.11 \\"
echo "    --compatible-architectures x86_64"
echo ""
echo "Then attach the layer to your Lambda function in the AWS Console or via CLI."
