<template>
  <div class="favorites-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>收藏管理</h2>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-filters">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索歌曲名称或歌手"
          clearable
          @input="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <!-- 管理员可以查看所有用户的收藏 -->
        <el-select
          v-if="currentUserIsAdmin"
          v-model="searchParams.userId"
          placeholder="选择用户"
          clearable
          @change="handleFilter"
          style="width: 200px; margin-left: 10px;"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          />
        </el-select>
      </div>
    </el-card>

    <!-- 收藏列表 -->
    <el-card>
      <el-table
        :data="filteredFavorites"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无收藏数据"
      >
        <el-table-column prop="song_name" label="歌曲名称" min-width="200" />
        <el-table-column prop="singer_name" label="歌手" min-width="150" />
        <el-table-column prop="album_name" label="专辑" min-width="150" />
        <el-table-column prop="created_at" label="收藏时间" min-width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                size="small" 
                type="danger" 
                @click="handleCancelFavorite(row)"
              >
                <el-icon><Delete /></el-icon>
                取消收藏
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { favoriteApi, userApi } from '../api'
import { isAdmin, getUserId } from '../utils/auth'
import { 
  Search, 
  Delete 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const favorites = ref([])
const users = ref([])

// 权限状态
const currentUserIsAdmin = ref(isAdmin())
const currentUserId = ref(getUserId())

// 搜索参数
const searchParams = reactive({
  keyword: '',
  userId: null
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 计算属性
const filteredFavorites = computed(() => {
  let filtered = favorites.value
  
  // 管理员未选择用户时，默认显示空列表
  if (currentUserIsAdmin.value && !searchParams.userId) {
    filtered = []
  }
  
  // 关键词搜索
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    filtered = filtered.filter(favorite => 
      favorite.song_name.toLowerCase().includes(keyword) ||
      favorite.singer_name.toLowerCase().includes(keyword)
    )
  }
  
  // 用户筛选
  if (searchParams.userId) {
    filtered = filtered.filter(favorite => favorite.user_id === searchParams.userId)
  }
  
  // 分页处理
  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  
  return filtered.slice(start, end)
})

// 生命周期
onMounted(() => {
  loadData()
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    // 管理员需要加载用户列表，普通用户不需要
    if (currentUserIsAdmin.value) {
      await Promise.all([loadFavorites(), loadUsers()])
    } else {
      // 普通用户直接加载自己的收藏
      await loadFavorites()
    }
  } catch (error) {
    ElMessage.error('数据加载失败')
    console.error('数据加载失败:', error)
  } finally {
    loading.value = false
  }
}

const loadFavorites = async () => {
  try {
    if (currentUserIsAdmin.value) {
      // 管理员可以查看所有收藏
      favorites.value = await favoriteApi.getAllFavorites()
    } else {
      // 普通用户只能查看自己的收藏
      favorites.value = await favoriteApi.getUserFavorites(currentUserId.value)
    }
  } catch (error) {
    throw new Error('加载收藏列表失败')
  }
}

const loadUsers = async () => {
  try {
    users.value = await userApi.getUsers()
  } catch (error) {
    throw new Error('加载用户列表失败')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleFilter = () => {
  pagination.currentPage = 1
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
}

const handleCancelFavorite = async (favorite) => {
  try {
    let message = ''
    if (currentUserIsAdmin.value) {
      message = `确定要取消用户"${favorite.username}"对歌曲"${favorite.song_name}"的收藏吗？`
    } else {
      message = `确定要取消对歌曲"${favorite.song_name}"的收藏吗？`
    }
    
    await ElMessageBox.confirm(
      message,
      '确认取消收藏',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await favoriteApi.deleteFavorite(favorite.id)
    ElMessage.success('取消收藏成功')
    await loadFavorites() // 重新加载收藏数据
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error('取消收藏失败')
    console.error('取消收藏失败:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.favorites-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-user-info {
  display: flex;
  align-items: center;
  margin-left: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border: 1px solid #e1f5fe;
  border-radius: 4px;
  color: #1890ff;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .favorites-container {
    padding: 10px;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-filters .el-input,
  .search-filters .el-select {
    width: 100% !important;
    margin-left: 0 !important;
  }
  
  .search-filters .current-user-info {
    margin-left: 0;
    margin-top: 10px;
    text-align: center;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .page-header h2 {
    text-align: center;
  }
}
</style>