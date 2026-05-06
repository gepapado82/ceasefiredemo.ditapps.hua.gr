<script>
import { defineComponent } from 'vue';
import CryptoJS from 'crypto-js';
const REPO_BASE = '/ceasefiredemo.ditapps.hua.gr';
  
function getPublicFiles() {
  // Get all files from the public directory using Vite's import.meta.glob
  const originalFiles = import.meta.glob('/public/classification/original/**/*.{png,jpg,jpeg}', { eager: true });

  const images = Object.keys(originalFiles).map(key => {
    const fileName = key.split('/').pop();
    const pathWithoutPublic = key.replace('/public', REPO_BASE);
    return {
      src: pathWithoutPublic,
      prediction: pathWithoutPublic.replace('/original/', '/predictions/'),
      name: fileName,
      // Extract class number from path (assuming format /class_X/)
      class: parseInt(key.match(/class_(\d+)/)?.[1] || '0')
    };
  });

  return images;
}

function getClassificationFiles() {
  // Get all .txt detection files from the public directory
  const detectionFiles = import.meta.glob('/public/detection/predictions/**/*.txt', {
    eager: true,
    as: 'raw'  // This tells Vite to import the raw content
  });

  // Group detections by filename (without extension)
  const grouped = {};

  Object.keys(detectionFiles).forEach(key => {
    const fileName = key.split('/').pop();
    const baseName = fileName.replace(/\.txt$/, '');
    const pathWithoutPublic = key.replace('/public', REPO_BASE);
    const content = detectionFiles[key].default || detectionFiles[key];

    // Split content into lines and remove empty lines
    const lines = content.split('\n').filter(line => line.trim());

    // First line contains metadata
    const [class_id, conf, entropy] = lines[0].split(' ').map(Number);

    // Next 5 lines contain top-5 classifications
    const top5 = lines.slice(1, 6).map(line => {
      const parts = line.split(' ');
      // If there's more than 2 parts, combine all but last for className
      const confidence = parseFloat(parts[parts.length - 1]);
      const className = parts.slice(0, -1).join(' ');
      return [className, confidence];
    });

    grouped[baseName] = {
      src: pathWithoutPublic,
      name: fileName,
      gt_class: parseInt(key.match(/class_(\d+)/)?.[1] || '0'),
      class_id: class_id,
      confidence: conf * 100,
      entropy: entropy * 100,
      top5
    };
  });

  console.log("Grouped classification files:", grouped);
  return grouped;
}


export default defineComponent({
  name: 'ImageTag',  // Changed from ImageLabel to ImageTag
  data() {
    const salt = 'a1b2c3d4';  // any constant string
    const clearText = 'ceasefiredemoSRE2025';
    // precompute hash + salt
    const STORED_HASH = CryptoJS.SHA256(clearText + salt).toString();
    return {
      pwInput: '',
      error: false,
      authenticated: false,
      salt,
      STORED_HASH,
      api_url: "/api/classify",
      api_top5: null,
      url_headers: ["Access-Control-Allow-Origin: *"],
      labels: ['Blades', 'Bombs', 'Bow and Arrow', 'Bullet Boxes', 'Bullet Cells',
        'Full_face_hoods', 'Injectable_Drug', 'Knives', 'Military_Clothing',
        'Pcp_airguns', 'Pils Drug', 'Pistols', 'Powder_Drug', 'Revolver',
        'Rifles', 'Rockets', 'Seeds', 'Shotgun', 'War Accessories',
        'Weapon_Cases', 'Weapon_Magazines', 'Weapon_Storage', 'Weeds'],
      all_filenames: null,
      staticImages: getPublicFiles(),
      staticClassifications: getClassificationFiles(),
      image_upload: null,
      loading: false,
      showModal: false,
      showInstructionsContent: true,
      uploadedImage: null,
      selectedFilters: [],
      gt_class: null,
      prediction_confidence: 0,
      prediction_entropy: 0,
    };
  },
  created() {
    this.authenticated = sessionStorage.getItem('fakeAuth') === 'true';
  },
  methods: {
    checkPassword() {
      // hash the input + same salt
      const inputHash = CryptoJS.SHA256(this.pwInput + this.salt).toString();
      if (inputHash === this.STORED_HASH) {
        this.authenticated = true;
        // sessionStorage.setItem('fakeAuth', 'true');
        this.error = false;
      } else {
        this.error = true;
      }
      this.pwInput = '';
    },
    logout() {
      this.authenticated = false;
      // sessionStorage.removeItem('fakeAuth');
    },
    quasarUploadImage(file) {
      if (!file || !file[0]) return;
      this.loading = true;
      const uploadedFile = file[0];
      this.image_upload = URL.createObjectURL(uploadedFile);
      this.sendImage(uploadedFile);
    },
    async loadExampleImage(imageSrc) {
      try {
        this.loading = true;
        this.showModal = true;

        // Get the filename from the path
        const fileName = imageSrc.split('/').pop().replace('.png', '').replace('.jpg', '');

        // Get the classification results
        const results = this.staticClassifications[fileName];
        if (!results) {
          console.error('No classification results found for:', fileName);
          return;
        }

        this.image_upload = imageSrc;
        this.api_top5 = results.top5.map(([className, confidence]) => [
          className,
          confidence // Keep original confidence value
        ]);
        this.gt_class = results.gt_class;
        this.prediction_confidence = results.confidence;
        this.prediction_entropy = results.entropy;

      } catch (error) {
        console.error('Error loading example image:', error);
      } finally {
        this.loading = false;
      }
    },
    resetImage() {
      this.image_upload = null;
      this.api_data = null;
      this.api_top5 = null;
      this.showModal = false;
    },
    toggleFilter(classIndex) {
      const index = this.selectedFilters.indexOf(classIndex);
      if (index === -1) {
        this.selectedFilters.push(classIndex);
      } else {
        this.selectedFilters.splice(index, 1);
      }
    },
    clearFilters() {
      this.selectedFilters = [];
    }
  },
  computed: {
    exampleImages() {
      if (!this.staticImages) return [];

      let filteredImages = this.staticImages;

      // Apply filters if any are selected
      if (this.selectedFilters.length > 0) {
        filteredImages = filteredImages.filter(image =>
          this.selectedFilters.includes(image.class)
        );
      }

      return filteredImages
        .map(image => ({
          ...image,
          description: `Ground Truth Class: ${this.labels[image.class]}`
        }))
        .sort(() => Math.random() - 0.5)
        .slice(0, 200);
    },
  }
});
</script>

<template>

  <q-page class="flex flex-center">
    <q-card v-if="!authenticated" class="login-card q-pa-md">
      <q-card-section class="text-center q-pb-md">
        <div class="text-h5 text-weight-bold q-mb-sm">Web image classification demo</div>
        <div class="text-h6 text-grey-8 text-weight-bold">Access Required</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="checkPassword">
          <q-input v-model="pwInput" type="password" label="Enter password" :error="error"
            error-message="Incorrect password" autofocus outlined class="q-mb-md" />
          <div class="row justify-center">
            <q-btn label="Submit" type="submit" color="primary" unelevated rounded class="full-width" />
          </div>
        </q-form>
      </q-card-section>
    </q-card>


    <div v-else class="full-width">
      <div class="text-h3 q-pa-md text-center">Web image classification demo</div>

      <div class="row justify-center q-mb-md">
        <div class="instructions-box text-body1" :class="{ 'minimized': !showInstructionsContent }">
          <div class="row items-center justify-between">
            <div class="text-h5 q-mr-sm"><b>Instructions</b></div>
            <q-btn flat round dense :icon="showInstructionsContent ? 'keyboard_arrow_down' : 'keyboard_arrow_up'"
              @click="showInstructionsContent = !showInstructionsContent" />
          </div>
          <div v-show="showInstructionsContent">
            <ul class="q-ma-none">
              <li><strong>Explore Example Images:</strong> Click on any image below to see how our AI model classifies
                different types of weapons and illicit items</li>
              <li><strong>Filter by Weapon Type:</strong> Use the filter buttons above the image grid to display only
                specific categories</li>
              <li><strong>Understanding the Results:</strong> When you click an image, a detailed results panel opens
                showing:
                <ul>
                  <li><strong>Ground Truth (Red):</strong> The correct weapon category</li>
                  <li><strong>AI Prediction (Blue):</strong> The model's top classification with confidence percentage
                  </li>
                  <li><strong>Top 5 Alternatives:</strong> The model's next best guesses ranked by confidence</li>
                  <li><strong>Performance Metrics:</strong> Model confidence (how certain the AI is) and entropy
                    (measure
                    of
                    prediction uncertainty)</li>
                </ul>
              </li>
              <li><strong>Compare Accuracy:</strong> See how well the AI prediction matches the ground truth to evaluate
                model performance</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Filtering -->
      <div class="filter-section q-mb-xl">
        <div class="text-subtitle1 q-mb-md text-grey-8 text-center">
          Filter images by weapon type
        </div>

        <div class="row justify-center">
          <div class="filter-container">
            <div class="row items-center q-gutter-sm q-pa-md">
              <q-icon name="filter_alt" size="24px" class="q-mr-md" color="primary" />
              <q-btn v-for="(label, index) in labels" :key="index" :label="label"
                :color="selectedFilters.includes(index) ? 'primary' : 'grey-4'"
                :text-color="selectedFilters.includes(index) ? 'white' : 'black'" @click="toggleFilter(index)" rounded
                class="filter-button" no-caps />
              <q-btn v-if="selectedFilters.length" label="Clear Filters" color="red-5" text-color="white"
                @click="clearFilters" rounded no-caps class="clear-button q-ml-lg" />
            </div>
          </div>
        </div>
      </div>

      <!-- Image grid -->
      <div class="row justify-center q-pa-md">
        <div class="col-12 col-md-11 col-xl-10">
          <div class="row justify-center q-col-gutter-md">
            <div v-for="(image, index) in exampleImages" :key="index" class="col-12 col-sm-6 col-md-4 col-lg-3">
              <q-card class="example-card cursor-pointer" @click="loadExampleImage(image.src)">
                <q-img :src="image.src" :ratio="1" spinner-color="primary" class="image-card">
                  <template v-slot:error>
                    <div class="absolute-full flex flex-center text-subtitle2">
                      Cannot load image
                    </div>
                  </template>
                  <!-- <div class="absolute-bottom text-subtitle2 text-center text-with-outline">
                  {{ image.description }}
                </div> -->
                </q-img>
              </q-card>
            </div>
          </div>
        </div>
      </div>

      <!-- Results modal -->
      <q-dialog v-model="showModal">
        <q-card class="modal-card">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h5 text-weight-bold q-ml-sm">Classification Results</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup @click="resetImage" class="q-mr-sm" />
          </q-card-section>

          <q-card-section horizontal class="content-section q-pa-md">
            <!-- Left side - Image section -->
            <q-card-section class="col-9 q-pr-md">
              <div v-if="loading" class="full-height column flex-center">
                <q-spinner color="primary" size="50px" />
              </div>
              <div v-else class="full-height">
                <div class="image-container">
                  <img :src="image_upload" />
                </div>
              </div>
            </q-card-section>

            <q-separator vertical />

            <!-- Right side - Classification Results -->
            <q-card-section class="col-3 detections-section">
              <div class="text-h6 text-weight-bold q-mb-md">Detected image type</div>

              <!-- Ground truth class -->
              <div class="text-subtitle2 q-mb-sm">Ground Truth Class</div>
              <div class="detection-button gt q-mb-lg">
                <div class="class-name">{{ labels[gt_class] }}</div>
              </div>

              <!-- Model predictions -->
              <div class="text-subtitle2 q-mb-sm">Model Predictions</div>
              <div class="text-caption q-mb-sm text-grey-8">
                Confidence: {{ prediction_confidence.toFixed(1) }}% |
                Entropy: {{ prediction_entropy.toFixed(1) }}%
              </div>
              <q-scroll-area style="height: calc(100% - 200px);">
                <q-list>
                  <div v-for="(item, i) in api_top5" :key="i" class="detection-button q-mb-sm"
                    :class="{ 'prediction': i === 0 }">
                    <div class="id-box">{{ i + 1 }}</div>
                    <div class="class-name">{{ item[0] }}</div>
                    <div class="confidence">{{ (item[1]).toFixed(1) }}%</div>
                  </div>
                </q-list>
              </q-scroll-area>
            </q-card-section>
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>
  </q-page>

</template>

<style scoped>
.my-card {
  width: 100%;
  max-width: 600px;
}

.selected_label {
  border: rgb(133, 22, 22);
  border-style: solid;
  background-color: rgba(133, 22, 22, 0.2);
  font-weight: bold;
}

.text-with-outline {
  color: #fff;
  text-shadow:
    0 0 6px #000,
    0 0 2px #000,
    1px 1px 2px #000,
    -1px -1px 2px #000;
  padding: 5px;
  font-weight: bold;
}

.minimal-padding {
  padding: 1.5px;
}

.full-height {
  height: 100%;
  min-height: 400px;
}

.detection-button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.detection-button.gt {
  background: rgba(255, 59, 59, 0.9);
  color: white;
}

.detection-button.prediction {
  background: rgba(0, 210, 255, 0.9);
  color: white;
}

.detection-button .id-box {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 6px;
  min-width: 32px;
  text-align: center;
  font-weight: bold;
}

.detection-button .class-name {
  flex-grow: 1;
  font-weight: 500;
}

.detection-button .confidence {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 10px;
  border-radius: 6px;
  min-width: 60px;
  text-align: center;
  font-weight: 500;
}

.detection-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.detection-button.gt:hover {
  background: rgba(255, 59, 59, 1);
}

.detection-button.prediction:hover {
  background: rgba(0, 220, 255, 1);
}

.filter-container {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: inline-block;
  margin: 0 auto;
}

.text-subtitle1 {
  font-weight: 400;
  letter-spacing: 0.01em;
}

.instructions-box {
  border: 1px solid rgba(255, 59, 59, 0.3);
  border-radius: 12px;
  background: rgba(255, 59, 59, 0.05);
  padding: 16px 24px;
  color: #666;
  line-height: 1.5;
  /* Remove max-width to allow full width */
  width: auto;
  transition: all 0.1s ease;
  max-width: 800px;
  margin: 0 auto;
}

.instructions-box ul {
  padding-left: 20px;
}

.instructions-box ul ul {
  margin-top: 4px;
}

.instructions-box li {
  margin-bottom: 4px;
}

.instructions-box.minimized {
  padding: 8px 24px;
}

.filter-section {
  background: rgba(0, 0, 0, 0.02);
  padding: 24px 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.filter-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.filter-button {
  min-width: 120px;
  transition: all 0.2s ease;
}

.filter-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clear-button {
  box-shadow: 0 2px 4px rgba(255, 59, 59, 0.2);
}

.clear-button:hover {
  box-shadow: 0 4px 8px rgba(255, 59, 59, 0.3);
}

.image-grid {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.image-card {
  transition: all 0.2s ease;
}

.image-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-card {
  width: 90vw;
  max-width: 1800px;
  height: 80vh;
  background: #fafafa;
}

.content-section {
  height: calc(100% - 50px);
}

.view-toggle-buttons {
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.view-toggle-buttons .q-btn {
  min-width: 150px;
  opacity: 0.7;
  transition: all 0.2s ease;
}

.view-toggle-buttons .q-btn.active {
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.image-container {
  height: calc(100% - 60px);
  background: #2d2d2d;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.detections-section {
  background: white;
  border-radius: 8px;
  height: 100%;
}

.example-card {
  height: 100%;
  width: 100%;
}

.image-card {
  height: 300px;
}

.row.justify-center {
  width: 100%;
}

.modal-card {
  width: 90vw;
  max-width: 1800px;
  height: 80vh;
  background: #fafafa;
}

.content-section {
  height: calc(100% - 50px);
}

.image-container {
  height: 100%;
  background: #2d2d2d;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.detections-section {
  background: white;
  border-radius: 8px;
  height: 100%;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Make sure the page takes full height for centering */
.q-page {
  min-height: 100vh;
}

.full-width {
  width: 100%;
}
</style>
