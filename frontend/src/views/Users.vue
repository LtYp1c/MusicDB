<template>
  <div class="users-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="handleAddUser">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-filters">
        <el-input
          v-model="searchParams.keyword"
          placeholder="搜索用户名或邮箱"
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

    <!-- 用户列表 -->
    <el-card>
      <el-table
        :data="filteredUsers"
        v-loading="loading"
        stripe
        style="width: 100%"
        empty-text="暂无用户数据"
      >
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              
              <el-button 
                v-if="row.id !== currentUserId" 
                size="small" 
                type="danger" 
                @click="handleDelete(row)"
              >
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

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="formDialog.visible"
      :title="formDialog.title"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="formDialog.data"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formDialog.data.username"
            placeholder="请输入用户名"
            maxlength="20"
            show-word-limit
            :disabled="formDialog.isEdit"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formDialog.data.email"
            placeholder="请输入邮箱地址"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!formDialog.isEdit">
          <el-input
            v-model="formDialog.data.password"
            type="password"
            placeholder="请输入密码"
            maxlength="20"
            show-word-limit
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword" v-if="!formDialog.isEdit">
          <el-input
            v-model="formDialog.data.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            maxlength="20"
            show-word-limit
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="formDialog.data.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
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
import { userApi } from '../api'
import { getUserId } from '../utils/auth'
import { 
  Plus, 
  Search, 
  Edit, 
  Delete 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const users = ref([])
const userFormRef = ref()
const currentUserId = ref(null)

// 搜索参数
const searchParams = reactive({
  keyword: '',
  role: null
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表单对话框
const formDialog = reactive({
  visible: false,
  title: '添加用户',
  loading: false,
  isEdit: false,
  data: {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  }
})

// 表单验证规则
const validatePassword = (rule, value, callback) => {
  if (!formDialog.isEdit && !value) {
    callback(new Error('请输入密码'))
  } else if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!formDialog.isEdit && !value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== formDialog.data.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 计算属性
const filteredUsers = computed(() => {
  let filtered = users.value
  
  // 关键词搜索
  if (searchParams.keyword) {
    const keyword = searchParams.keyword.toLowerCase()
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(keyword) ||
      user.email.toLowerCase().includes(keyword)
    )
  }
  
  // 角色筛选
  if (searchParams.role) {
    filtered = filtered.filter(user => user.role === searchParams.role)
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
  currentUserId.value = getUserId()
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    await loadUsers()
  } catch (error) {
    ElMessage.error('数据加载失败')
    console.error('数据加载失败:', error)
  } finally {
    loading.value = false
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

const handleAddUser = () => {
  formDialog.title = '添加用户'
  formDialog.isEdit = false
  formDialog.data = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'user'
  }
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    userFormRef.value?.clearValidate()
  })
}

const handleEdit = (user) => {
  formDialog.title = '编辑用户'
  formDialog.isEdit = true
  formDialog.data = { 
    ...user,
    password: '',
    confirmPassword: ''
  }
  formDialog.visible = true
  
  // 清除表单验证
  nextTick(() => {
    userFormRef.value?.clearValidate()
  })
}

const handleSave = async () => {
  try {
    // 表单验证
    await userFormRef.value.validate()
    
    formDialog.loading = true
    
    const { confirmPassword, ...submitData } = formDialog.data
    
    if (formDialog.isEdit) {
      // 编辑用户时，如果没有输入密码，则不更新密码字段
      if (!submitData.password) {
        delete submitData.password
      }
      await userApi.updateUser(submitData.id, submitData)
      ElMessage.success('用户更新成功')
    } else {
      await userApi.createUser(submitData)
      ElMessage.success('用户添加成功')
    }
    
    formDialog.visible = false
    await loadUsers() // 重新加载用户数据
  } catch (error) {
    if (error && error.errors) {
      // 表单验证错误，不显示错误消息
      return
    }
    ElMessage.error(formDialog.isEdit ? '更新失败' : '添加失败')
    console.error('保存失败:', error)
  } finally {
    formDialog.loading = false
  }
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${user.username}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await userApi.deleteUser(user.id)
    ElMessage.success('删除成功')
    await loadUsers() // 重新加载用户数据
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
.users-container {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .users-container {
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