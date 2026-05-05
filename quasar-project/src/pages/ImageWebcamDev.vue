<script>
import { defineComponent } from 'vue';
import * as ort from 'onnxruntime-web';
import { Jimp } from 'jimp';

export default defineComponent({
  name: 'ImageLabel',
  data() {
    return {
      // preview: null,
      image_upload: null,
      // api_response: null,
      api_data: null,
      api_confidence: null,
      // image_tag: null,
      // api_url: "http://10.100.52.103:8000/predict_vis",
      url_headers: ["Access-Control-Allow-Origin: *"],
      labels: ['Blades', 'Bombs', 'Bow and Arrow', 'Bullet Boxes', 'Bullet Cells', 'Full_face_hoods', 'Injectable_Drug', 'Knives', 'Military_Clothing', 'Pcp_airguns', 'Pils Drug', 'Pistols', 'Powder_Drug', 'Revolver', 'Rifles', 'Rockets', 'Seeds', 'Shotgun', 'War Accessories', 'Weapon_Cases', 'Weapon_Magazines', 'Weapon_Storage', 'Weeds'],
    };
  },
  methods: {
    quasarUploadImage(file) {
      console.log(file.length);
      // this.image_upload = URL.createObjectURL(file[0]);
      // this.sendImage(file[0]);
      // // return this.api_url;

      // const tensorTest = ort.Tensor(file);
      console.log("file: ", file[0]);
      const image = Jimp.read(file.tempFilePath).then((imageBuffer) => {
        return imageBuffer.resize(224, 224);
      });
      console.log("Image: ", image);

    },
    // previewImage: function (event) {
    //   console.log(this.image.value);
    //   let input = event.target;
    //   if (input.file) {
    //     let reader = new FileReader();
    //     reader.onload = (e) => {
    //       this.preview = e.target.result;
    //     };
    //     this.image = input.files[0];
    //     reader.readAsDataURL(input.files[0]);
    //   }
    // },
    resetImage: function () {
      this.image = null;
      this.preview = null;
    },
    async sendImage(file) {
      let base_url = 'http://10.100.52.103:8000/';
      let endpoint = 'classify';
      let api_url = base_url + endpoint;
      console.log(api_url);

      const formdata = new FormData();

      console.log("Uploaded Image:", file);
      console.log("Uploaded Image Name:", file.name);

      formdata.append("files", file, file.name);

      const requestOptions = {
        method: "POST",
        body: formdata,
        redirect: "follow",
      };

      const response = await fetch(api_url, requestOptions);

      const json = await response.json();
      const label = json["results"][0]["predicted_label"];
      this.api_data = this.labels[label];
      this.api_confidence = json["results"][0]["confidence"];
      // console.log("API Response Status:", this.api_data);
    },
    handleUploadedImage(files) {
      // const response = files.xhr.response;
      // console.log("Response:", response);
      // this.api_data = response;
    },
  }
});
</script>

<template>
  <div class="text-h6 q-pa-md">Κατηγοριοποίηση εικόνας</div>

  <div class="row">
    <div class="col-6">
      <div class="q-pa-md q-gutter-sm">
        <q-banner rounded class="bg-blue-grey-2">
          Σε αυτό το service, μεταφορτώστε μια εικόνα για να λάβετε το σχετικό tag (κλάση)
        </q-banner>
      </div>
    </div>
  </div>

  <!--  https://stackoverflow.com/questions/74166043/q-file-element-image-upload-preview-not-displaying-correctly-->

  <div class="q-pa-md q-gutter-sm">
    <q-uploader no-thumbnails color="blue-grey-10" label="Upload an image" name="image_upload" :url="quasarUploadImage"
      :headers="url_headers" method="POST" field-name="file" accept=".jpg, .png, .webp, image/*" max-files="1"
      @uploaded="handleUploadedImage" />
  </div>

  <div class="q-pa-md q-gutter-md">
    <template v-if="api_data">
      <div class="text-subtitle2">Το μοντέλο Τ.Ν. κατηγοριοποίησε την εικόνα ως την εξής κλάση: </div>
      <div class="row">
        <q-card>
          <!-- <q-card-section class="q-pa-md q-gutter-sm">
        </q-card-section> -->
          <q-card-section horizontal class="items-center justify-center">
            <q-card-section>
              <img :src=this.image_upload style="max-width: 100%;" />
            </q-card-section>

            <q-card-section class="q-pa-md q-gutter-sm">
              <q-btn disable outline rounded size="lg"> {{ Math.round(this.api_confidence *
                100) }}% {{ this.api_data }}</q-btn>
            </q-card-section>
          </q-card-section>

        </q-card>
      </div>

    </template>
  </div>

</template>

<style scoped>
.my-card {
  width: 100%;
  max-width: 600px;
}
</style>
