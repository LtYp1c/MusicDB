<template>
  <div class="singers-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <h2>{{ isAdminComputed ? '歌手管理' : '歌手列表' }}</h2>
      <el-button v-if="isAdminComputed" type="primary" @click="handleAddSinger">
        <el-icon><Plus /></el-icon>
        添加歌手
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-filters">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索歌手名称"
          clearable
          @input="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </el-card>

    <!-- 歌手列表 -->
    <el-card>
      <el-table
        :data="filteredSingers"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无歌手数据"
      >
        <el-table-column prop="name" label="歌手姓名" min-width="200" />
        <el-table-column prop="nationality" label="国籍" min-width="120" />
        <el-table-column prop="birth_date" label="出生日期" min-width="120">
          <template #default="{ row }">
            {{ formatDate(row.birth_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="albums_count" label="专辑数量" width="100" />
        <el-table-column prop="songs_count" label="歌曲数量" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button v-if="!isAdminComputed" size="small" @click="handleViewDetail(row)">
                 <el-icon><View /></el-icon>
                 查看详情
               </el-button>
               
              <el-button v-if="isAdminComputed" size="small" @click="handleEdit(row)">
                 <el-icon><Edit /></el-icon>
                 编辑
               </el-button>
               
               <el-button v-if="isAdminComputed" size="small" type="danger" @click="handleDelete(row)">
                 <el-icon><Delete /></el-icon>
                 删除
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

    <!-- 歌手详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      :title="detailDialog.title"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="detailDialog.data" class="singer-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="歌手姓名">
            {{ detailDialog.data.name }}
          </el-descriptions-item>
          <el-descriptions-item label="国籍">
            {{ detailDialog.data.nationality || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="出生日期">
            {{ formatDate(detailDialog.data.birth_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="专辑数量">
            {{ detailDialog.data.albums_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="歌曲数量">
            {{ detailDialog.data.songs_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="简介" :span="2">
            <div class="description-content">
              {{ detailDialog.data.description || '暂无简介' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑歌手对话框 -->
    <el-dialog
      v-model="formDialog.visible"
      :title="formDialog.title"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="singerFormRef"
        :model="formDialog.data"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="歌手姓名" prop="name">
          <el-input
            v-model="formDialog.data.name"
            placeholder="请输入歌手姓名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="国籍">
          <el-input
            v-model="formDialog.data.nationality"
            placeholder="请输入国籍"
            maxlength="20"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="出生日期">
          <el-date-picker
            v-model="formDialog.data.birth_date"
            type="date"
            placeholder="选择出生日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="头像URL">
          <el-input
            v-model="formDialog.data.avatar"
            placeholder="请输入头像URL"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="简介">
          <el-input
            v-model="formDialog.data.description"
            type="textarea"
            :rows="4"
            placeholder="请输入歌手简介"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="formDialog.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { singerApi } from '../api'
import { isAdmin } from '../utils/auth'
import { 
  View, 
  Plus, 
  Search, 
  Edit, 
  Delete 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const singers = ref([])
const singerFormRef = ref()

// 搜索参数
const searchParams = reactive({
  keyword: '',
  nationality: null
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 详情对话框
const detailDialog = reactive({
  visible: false,
  title: '歌手详情',
  data: null
})

// 表单对话框
const formDialog = reactive({
  visible: false,
  title: '添加歌手',
  loading: false,
  data: {
    name: '',
    nationality: '',
    birth_date: null,
    avatar: '',
    description: ''
  }
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入歌手姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '歌手姓名长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const isAdminComputed = computed(() => isAdmin())

const filteredSingers = computed(() => {
  let filtered = singers.value
  
  // 关键词搜索
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    filtered = filtered.filter(singer => 
      singer.name.toLowerCase().includes(keyword)
    )
  }
  
  // 国籍筛选
  if (searchParams.nationality) {
    filtered = filtered.filter(singer => singer.nationality === searchParams.nationality)
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
    await loadSingers()
  } catch (error) {
    ElMessage.error('数据加载失败')
    console.error('数据加载失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSingers = async () => {
  try {
    singers.value = await singerApi.getSingers()
  } catch (error) {
    throw new Error('加载歌手列表失败')
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

const handleViewDetail = (singer) => {
  detailDialog.data = { ...singer }
  detailDialog.visible = true
}

const handleAddSinger = () => {
  formDialog.title = '添加歌手'
  formDialog.data = {
    name: '',
    nationality: '',
    birth_date: null,
    avatar: '',
    description: ''
  }
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    singerFormRef.value?.clearValidate()
  })
}

const handleEdit = (singer) => {
  formDialog.title = '编辑歌手'
  formDialog.data = { ...singer }
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    singerFormRef.value?.clearValidate()
  })
}

const handleSave = async () => {
  try {
    // 表单验证
    await singerFormRef.value.validate()
    
    formDialog.loading = true
    
    const isEdit = formDialog.title === '编辑歌手'
    
    if (isEdit) {
      await singerApi.updateSinger(formDialog.data.id, formDialog.data)
      ElMessage.success('歌手更新成功')
    } else {
      await singerApi.createSinger(formDialog.data)
      ElMessage.success('歌手添加成功')
    }
    
    formDialog.visible = false
    await loadSingers() // 重新加载歌手数据
  } catch (error) {
    if (error && error.errors) {
      // 表单验证错误，不显示错误消息
      return
    }
    ElMessage.error(formDialog.title === '编辑歌手' ? '更新失败' : '添加失败')
    console.error('保存失败:', error)
  } finally {
    formDialog.loading = false
  }
}

const handleDelete = async (singer) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除歌手"${singer.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await singerApi.deleteSinger(singer.id)
    ElMessage.success('删除成功')
    await loadSingers() // 重新加载歌手数据
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.singers-container {
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

.singer-detail-content {
  line-height: 1.6;
}

.description-content {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.8;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .singers-container {
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