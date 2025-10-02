import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/passivos',
    name: 'passivos',
    component: () => import('../views/PassivosView.vue'),
  },
  {
    path: '/renda-variavel',
    name: 'renda-variavel',
    component: () => import('../views/RendaVariavelView.vue'),
  },
  {
    path: '/renda-fixa',
    name: 'renda-fixa',
    component: () => import('../views/RendaFixaView.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
