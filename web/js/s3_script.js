// s3 client
var s3 = new AWS.S3({
    params: { Bucket: '<YOUR BUCKET>' }
});

function uploadContent() {
    let files = document.getElementById('user_file').files;

    if (!files.length) {
        return alert('Please choose a file to upload first.');
    } else {
        let file = files[0];

        if (file.type === 'image/jpeg' || file.type === 'video/mp4') {
            let photoKey = file.name;

            s3.upload({
                Key: photoKey,
                Body: file,
                ACL: 'public-read'
            }, {
                partSize: 10 * 1024 * 1024,
                queueSize: 1
            }, function (err, data) {
                if (err) {
                    return alert('There was an error uploading your photo: ', err.message);
                }
                alert('Successfully uploaded!');
            });
        } else {
            alert('Please choose .jpg or .mp4 files.')
        }

    }
}