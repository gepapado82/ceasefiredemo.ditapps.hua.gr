<script>
export default {
  name: "SimilarImage",
  data() {
    return {
      api_url: "http://10.100.52.103:8000/predict_static",
      url_headers: ["Access-Control-Allow-Origin: *", "mode: no-cors"],
      image_count: null,
      image_list: null,
    };
  },
  methods: {
    quasarUploadImage(files) {
      console.log(files.length);
      this.getSimilarImages(files[0]);
      // return this.api_url;
    },
    async getSimilarImages(file) {
      let base_url = 'http://10.100.52.103:8000/';
      let endpoint = 'classify_static';
      let num_images = this.image_count;
      let api_url = base_url + endpoint + "?num_images=" + num_images;
      console.log(api_url);

      const formdata = new FormData();

      formdata.append("file", file, file.name);

      const requestOptions = {
        method: "POST",
        body: formdata,
        redirect: "follow",
      };

      const result = await fetch(api_url, requestOptions);
      const similarImages = await result.json();
      const similarImagesList = similarImages["files"];

      console.log("Similar Images:", similarImagesList);

      const similarImagesURLs = similarImagesList.map((x) => base_url + x);
      console.log("Similar Images URLS:", similarImagesURLs);

      this.image_list = similarImagesURLs.map((x) => {
        return {
          img_src: x,
          name: "Image",
          brand: "Brand",
        };
      });

    },
    async getRandomImage() {
      // let response = await fetch("https://api.api-ninjas.com/v1/randomimage?category=technology", {method: "GET", mode: "no-cors", headers: {"X-Api-Key": "53MdYc1WN6MSjm5wg+7QOA==uRs2Omvh6AMf7hIa", "Accept": "image/jpg"}})
      let response = await fetch("https://picsum.photos/500/300");
      console.log("random image fetch");
      console.log(response.url);
      let image_url = response.url;
      return image_url;
    }
  }
};
</script>

<template>
  <div class="text-h5 q-pa-md">Παρόμοιες εικόνες Web-Crawled</div>

  <div class="row">
    <div class="col-6">
      <div class="q-pa-md q-gutter-sm">
        <q-banner rounded class="bg-blue-grey-2">
          <!--          In this service you will upload an image and receive similar images from the A.I. Model-->
          Σε αυτό το service μεταφορτώστε μια εικόνα για να λάβετε εικόνες με παρόμοιο περιεχόμενο.
        </q-banner>
      </div>
    </div>
  </div>

  <div class="q-pa-md q-gutter-sm">
    <q-input v-model="image_count" type="number" outlined placeholder="Select from 1-20"
      label="Insert the number of images to return" style="max-width: 300px" />
    <q-uploader color="blue-grey-10" label="Upload an image" name="image_upload" :url="quasarUploadImage"
      :headers="url_headers" accept=".jpg, .png, image/*" max-files="1" />
  </div>

  <div class="q-pa-md q-gutter-sm row">
    <template v-if="image_list">
      <div>
        <div class="text-subtitle2">Το μοντέλο Τ.Ν κατηγοριοποίησε την εικόνα και βρήκε τις παρακάτω παρόμοιες εικόνες:
        </div>
      </div>

      <div class="q-pa-sm row items-start q-gutter-md">
        <div v-for="(image, index) in image_list" v-bind:key="index">
          <q-card 
            style="min-width: 500px;"
            class="my-card"
          >
            <!--          <img src="https://random.imagecdn.app/500/150">-->
            <img :src=image.img_src />
          </q-card>
        </div>
      </div>
    </template>
  </div>

</template>

<style scoped>
.my-card {
  width: 100%;
  max-width: 500px;
}
</style>
