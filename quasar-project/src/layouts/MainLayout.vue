<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="xxbg-red-10" style="background-color: rgb(133, 22, 22);">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          CEASEFIRE
        </q-toolbar-title>

      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" bordered>
      <q-list>
        <q-item-label header>
          Menu
        </q-item-label>

        <EssentialLink v-for="link in essentialLinks" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue';
import EssentialLink from 'components/EssentialLink.vue';

const linksList = [
  {
    title: 'Home',
    caption: '',
    icon: 'home',
    target: '',
    link: '/#'
  },
  {
    title: 'X-ray illicit firearms detection',
    // caption: 'X-ray Object Detection',
    icon: 'code',
    target: '',
    link: '/#/object-detection'
  },
  {
    title: 'Image Classification',
    // caption: 'Image Classification',
    icon: 'code',
    target: '',
    link: '/#/image-classification'
  },
  // {
  //   title: 'Παρόμοιες εικόνες X-ray',
  //   // caption: 'Similar X-ray Images',
  //   icon: 'image',
  //   target: '',
  //   link: '/#/similar-xray'
  // },
  // {
  //   title: 'Παρόμοιες εικόνες Web-Crawled',
  //   // caption: 'Similar Web-Crawled Images',
  //   icon: 'image',
  //   target: '',
  //   link: '/#/similar-images'
  // },
  // {
  //   title: 'Εικόνες X-ray ανά κλάση',
  //   // caption: 'X-ray images by class',
  //   icon: 'image',
  //   target: '',
  //   link: '/#/xray-tag'
  // },
  // {
  //   title: 'Εικόνες Web-Crawled ανά κλάση',
  //   // caption: 'Web-Crawled images by class',
  //   icon: 'image',
  //   target: '',
  //   link: '/#/image-tag'
  // },
  // {
  //   title: 'Webcam DEV',
  //   // caption: 'Web-Crawled images by class',
  //   icon: 'image',
  //   target: '',
  //   link: '/#/image-webcam'
  // },
  {
    title: 'Project Ceasefire',
    icon: 'school',
    target: '_blank',
    link: 'https://ceasefire-project.eu/'
  },
];

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink
  },

  setup() {
    const leftDrawerOpen = ref(false);

    return {
      essentialLinks: linksList,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      }
    };
  }
});
</script>
