
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: '/object-detection', component: () => import('pages/ImageLabel.vue') },
      // { path: '/similar-xray', component: () => import('pages/SimilarImage.vue') },
      // { path: '/xray-tag', component: () => import('pages/TagImage.vue') },
      { path: '/image-classification', component: () => import('pages/ImageTag.vue') },
      // { path: '/similar-images', component: () => import('pages/SimilarImage2.vue') },
      // { path: '/image-tag', component: () => import('pages/TagImage2.vue') },
      // { path: '/image-webcam', component: () => import('pages/ImageWebcamDev.vue') },

    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
];

export default routes;
