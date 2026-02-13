import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Songs from '../views/Songs.vue'
import Singers from '../views/Singers.vue'
import Albums from '../views/Albums.vue'
import Users from '../views/Users.vue'
import Favorites from '../views/Favorites.vue'
import Playlists from '../views/Playlists.vue'
import PlaylistDetail from '../views/PlaylistDetail.vue'
import Login from '../views/Login.vue'
import { getRole, isAdmin, isAuthed } from '../utils/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard
  },
  {
    path: '/songs',
    name: 'songs',
    component: Songs
  },
  {
    path: '/singers',
    name: 'singers',
    component: Singers
  },
  {
    path: '/albums',
    name: 'albums',
    component: Albums
  },
  {
    path: '/users',
    name: 'users',
    component: Users,
    meta: { requiresAdmin: true }
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: Favorites
  },
  {
    path: '/playlists',
    name: 'playlists',
    component: Playlists
  },
  {
    path: '/playlists/:id',
    name: 'playlist-detail',
    component: PlaylistDetail
  },

]
// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})
// 权限控制
router.beforeEach((to, from, next) => {
  if (to.name === 'login') return next()
  if (!isAuthed()) return next({ name: 'login' })

  if (to.meta && to.meta.requiresAdmin && !isAdmin()) {
    return next({ name: 'dashboard' })
  }
  next()
})

export default router