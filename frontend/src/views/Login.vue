<template>
  <div class="login">
    <el-card class="login-card">
      <template #header>
        <span>登录</span>
      </template>

      <el-form :model="form" label-width="80px">
        <el-form-item label="身份">
          <el-radio-group v-model="form.role">
            <el-radio-button label="admin">管理员</el-radio-button>
            <el-radio-button label="user">普通用户</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号（用户名）" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="doLogin" :loading="logging">登录</el-button>
          <el-button v-if="form.role === 'user'" @click="showRegisterDialog" style="margin-left: 10px;">注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 注册对话框 -->
    <el-dialog
      v-model="registerDialogVisible"
      title="用户注册"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            maxlength="20"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            maxlength="20"
            show-word-limit
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-word-limit
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doRegister" :loading="registering">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { setAuth } from '../utils/auth'
import { authApi, userApi } from '../api'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        role: 'user',
        username: '',
        password: ''
      },
      logging: false,
      registerDialogVisible: false,
      registering: false,
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      registerFormRef: null
    }
  },
  computed: {
    registerRules() {
      const validatePassword = (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入密码'))
        } else if (value.length < 6) {
          callback(new Error('密码长度不能少于6位'))
        } else {
          callback()
        }
      }

      const validateConfirmPassword = (rule, value, callback) => {
        if (!value) {
          callback(new Error('请再次输入密码'))
        } else if (value !== this.registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }

      return {
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
          { required: true, message: '请输入密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        confirmPassword: [
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    async doLogin() {
      if (!this.form.username || !this.form.password) {
        this.$message.error('请输入账号和密码')
        return
      }
      this.logging = true
      try {
        const res = await authApi.login({ 
          username: this.form.username, 
          password: this.form.password,
          role: this.form.role
        })
        const userId = res.id
        const role = res.role || 'user'
        setAuth({ userId, role, username: res.username })
        this.$message.success('登录成功')
        
        // 触发权限状态更新事件
        window.dispatchEvent(new Event('authStateChanged'))
        
        this.$router.replace('/dashboard')
      } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
          this.$message.error(`登录失败：${e.response.data.error}`)
        } else {
          this.$message.error('登录失败：用户名或密码错误')
        }
      } finally {
        this.logging = false
      }
    },
    
    showRegisterDialog() {
      this.registerDialogVisible = true
      this.registerForm = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
      this.$nextTick(() => {
        if (this.registerFormRef) {
          this.registerFormRef.clearValidate()
        }
      })
    },
    
    async doRegister() {
      try {
        // 确保表单引用存在
        if (!this.registerFormRef) {
          this.registerFormRef = this.$refs.registerFormRef
        }
        
        // 表单验证
        await this.registerFormRef.validate()
        
        this.registering = true
        
        // 调用注册API
        const { confirmPassword, ...registerData } = this.registerForm
        await userApi.createUser(registerData)
        
        this.$message.success('注册成功！请使用新账号登录')
        this.registerDialogVisible = false
        
        // 自动填充用户名到登录表单
        this.form.username = this.registerForm.username
        this.form.password = ''
      } catch (error) {
        if (error && error.response && error.response.data && error.response.data.error) {
          this.$message.error(`注册失败：${error.response.data.error}`)
        } else if (error && error.errors) {
          // 表单验证错误，不显示额外消息
          return
        } else {
          this.$message.error('注册失败，请稍后重试')
        }
        console.error('注册失败:', error)
      } finally {
        this.registering = false
      }
    }
  },
  
  mounted() {
    // 获取表单引用
    this.registerFormRef = this.$refs.registerFormRef
  }
}
</script>

<style scoped>
.login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
}

.login-card {
  width: 420px;
}
</style>