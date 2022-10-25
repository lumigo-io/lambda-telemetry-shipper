echo "Extension layer"
echo "-Installing the package and its dependencies"
python -W ignore setup.py --quiet bdist_wheel  # create .egg-info
enc_location=../common-resources/encrypted_files/credentials_production.enc
mkdir -p ~/.aws
echo ${KEY} | gpg --batch -d --passphrase-fd 0 ${enc_location} > ~/.aws/credentials
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
pushd src > /dev/null || exit

echo "-create directories to zip"
echo "--extension"
mkdir extensions
cp ../scripts/telemetry extensions/

echo "--shipper"
mkdir extension-python-modules
cp -R lambda_telemetry_shipper.egg-info extension-python-modules/
cp -R lambda_telemetry_shipper extension-python-modules/

echo "--python runtime"
aws s3 cp --quiet s3://lumigo-runtimes/python/python-runtime-38.zip runtime.zip
unzip -q runtime.zip
mv python python-runtime

echo "-zipping"
zip -qr "extensions.zip" "extensions" "extension-python-modules" "python-runtime"


echo "-publish"
regions=("us-west-2")
layer_name="lumigo-telemetry-shipper"
for region in "${regions[@]}"; do
    version=$(aws lambda publish-layer-version --layer-name "${layer_name}" --description "No-code to ship your telemetry logs" --zip-file fileb://extensions.zip --region ${region} --cli-connect-timeout 6000 | jq -r '.Version')
    aws lambda add-layer-version-permission --layer-name "${layer_name}" --statement-id engineering-org --principal "*" --action lambda:GetLayerVersion --version-number ${version} --region ${region} > /dev/null
    echo "published layer version: ${version} in region: ${region}"
    echo "arn:aws:lambda:${region}:723663554526:layer:${layer_name}:${version}"
done
rm -rf extensions extension-python-modules extensions.zip runtime.zip python-runtime __MACOSX
popd > /dev/null || exit


echo "-update README"
sed -i "s/\(arn:aws:lambda:<region>:114300393969:layer:${layer_name}:\)[0-9]*/\1${version}/" README.md
git add README.md || true
git commit -m"update layer ARN in README [skip ci]" || true
git push origin main || true

echo
echo "Done! Latest version: ${version}"
echo
