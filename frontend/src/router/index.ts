import { createRouter, createWebHistory } from 'vue-router';
import type { RendaVariavelCategory } from '../types/rendaVariavel';

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
    redirect: '/renda-variavel/acoes',
  },
  {
    path: '/renda-variavel/:category(acoes|fiis|stocks|reits|etf)',
    name: 'renda-variavel-categoria',
    component: () => import('../views/RendaVariavelView.vue'),
    props: (route) => ({ category: route.params.category as RendaVariavelCategory }),
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
