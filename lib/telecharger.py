from minio import Minio

client = Minio(
    "object.files.data.gouv.fr"
)

bucket = "meteofrance-drias"
prefix = "SocleM-Climat-2025/CPRCM/METROPOLE/ALPX-3/CNRM-ESM2-1/r1i1p1f2/CNRM-AROME46t1/ssp370/day/tasAdjust/version-hackathon-102025/"

# Lister et télécharger tous les fichiers
objects = client.list_objects(bucket, prefix=prefix, recursive=True)
for obj in objects:
    print("Téléchargement de", obj.object_name)
    client.fget_object(bucket, obj.object_name, obj.object_name.split("/")[-1])
