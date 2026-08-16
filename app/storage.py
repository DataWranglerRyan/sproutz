from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings
from flask import current_app


class PlantPhotoError(ValueError):
    """Raised when a plant photo cannot be validated or stored."""


IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
)


def get_image_content_type(photo_file):
    header = photo_file.stream.read(16)
    photo_file.stream.seek(0)

    for signature, content_type in IMAGE_SIGNATURES:
        if header.startswith(signature):
            return content_type
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"
    raise PlantPhotoError("Choose a JPEG, PNG, or WebP image.")


def get_container_client():
    connection_string = current_app.config["AZURE_STORAGE_CONNECTION_STRING"]
    container_name = current_app.config["AZURE_STORAGE_CONTAINER"]
    if not connection_string or not container_name:
        raise PlantPhotoError(
            "Photo storage is not configured. Add the Azure Storage settings first."
        )
    return BlobServiceClient.from_connection_string(
        connection_string
    ).get_container_client(container_name)


def plant_photo_blob_name(plant_id):
    return f"plants/{plant_id}/photo"


def upload_plant_photo(plant_id, photo_file):
    if not photo_file or not photo_file.filename:
        raise PlantPhotoError("Choose a photo to upload.")

    content_type = get_image_content_type(photo_file)
    blob_name = plant_photo_blob_name(plant_id)
    try:
        get_container_client().upload_blob(
            name=blob_name,
            data=photo_file.stream,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
    except AzureError as error:
        current_app.logger.exception(
            "Azure Blob upload failed for plant %s.", plant_id
        )
        raise PlantPhotoError("Unable to upload the photo. Please try again.") from error
    return blob_name


def download_plant_photo(blob_name):
    try:
        blob_client = get_container_client().get_blob_client(blob_name)
        content_type = blob_client.get_blob_properties().content_settings.content_type
        return blob_client.download_blob().readall(), content_type
    except ResourceNotFoundError as error:
        raise PlantPhotoError("This photo is no longer available.") from error
    except AzureError as error:
        raise PlantPhotoError("Unable to load the photo. Please try again.") from error


def delete_plant_photo(blob_name):
    try:
        get_container_client().delete_blob(blob_name)
    except ResourceNotFoundError:
        return
    except AzureError as error:
        raise PlantPhotoError("Unable to remove the plant photo.") from error
