<template>
  <div class="space-y-6 max-w-5xl mx-auto py-4">

    <!-- 상단 헤더 + 글쓰기 버튼 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center" style="background-color: var(--church-navy);">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 12h6" />
          </svg>
        </div>
        <div>
          <h2 class="text-xl font-bold" style="color: var(--church-navy);">게시판</h2>
          <p class="text-xs text-gray-500 mt-0.5">질의응답, 오류수정요청 등 소통의 공간입니다. <span class="text-gray-400 ml-1">(총 {{ posts.length }}개의 게시글)</span></p>
        </div>
      </div>
      <button
        @click="openWriteForm"
        class="flex items-center px-4 py-2 rounded-lg text-sm font-semibold text-white shadow-md transition-all hover:opacity-90"
        style="background-color: var(--church-navy);"
      >
        <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        글쓰기
      </button>
    </div>

    <!-- 로딩 -->
    <div v-if="isLoading" class="text-center py-12 text-gray-400">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-blue-500 mb-3"></div>
      <p class="text-sm">게시판을 불러오는 중...</p>
    </div>

    <!-- 게시글 없음 -->
    <div v-else-if="posts.length === 0" class="card-church p-12 text-center">
      <div class="w-14 h-14 mx-auto rounded-full bg-gray-100 flex items-center justify-center mb-4">
        <svg class="w-7 h-7 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p class="text-gray-400 text-sm">아직 게시글이 없습니다. 첫 글을 남겨보세요!</p>
    </div>

    <!-- 게시글 목록 -->
    <div v-else class="card-church overflow-hidden">
      <!-- 목록 헤더 -->
      <div class="hidden sm:grid grid-cols-12 px-5 py-3 text-xs font-semibold uppercase tracking-wider border-b"
           style="color: var(--church-gray); background-color: var(--church-cream); border-color: var(--church-light-gray);">
        <div class="col-span-1 text-center">번호</div>
        <div class="col-span-2 text-center">분류</div>
        <div class="col-span-5">제목</div>
        <div class="col-span-2 text-center">작성자</div>
        <div class="col-span-2 text-center">작성일</div>
      </div>

      <!-- 게시글 행 -->
      <div
        v-for="(post, idx) in posts"
        :key="post.row_key"
        @click="openPost(post)"
        class="grid grid-cols-12 items-center px-5 py-3.5 border-b cursor-pointer hover:bg-gray-50 transition-colors text-sm"
        style="border-color: var(--church-light-gray);"
      >
        <div class="col-span-1 text-center text-gray-400 text-xs">{{ posts.length - idx }}</div>
        <div class="col-span-2 flex justify-center">
          <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="categoryClass(post.category)">
            {{ post.category }}
          </span>
        </div>
        <div class="col-span-5 font-medium truncate" style="color: var(--church-navy);">{{ post.title }}</div>
        <div class="col-span-2 text-center text-gray-500 text-xs">{{ post.author }}</div>
        <div class="col-span-2 text-center text-gray-400 text-xs">{{ formatDate(post.created_at) }}</div>
      </div>
    </div>

    <!-- ===== 모달 ===== -->

    <!-- 글 상세보기 모달 -->
    <div v-if="viewingPost" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="closePost">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div class="flex items-center space-x-2">
            <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="categoryClass(viewingPost.category)">{{ viewingPost.category }}</span>
            <h3 class="text-base font-bold" style="color: var(--church-navy);">{{ viewingPost.title }}</h3>
          </div>
          <button @click="closePost" class="text-gray-400 hover:text-gray-600 p-1">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="px-6 py-2 flex items-center justify-between text-xs text-gray-400 border-b border-gray-50">
          <span>작성자: <strong class="text-gray-600">{{ viewingPost.author }}</strong></span>
          <span>{{ formatDate(viewingPost.created_at) }}{{ viewingPost.updated_at !== viewingPost.created_at ? ' (수정됨)' : '' }}</span>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-5">
          <p class="text-sm leading-loose whitespace-pre-wrap" style="color: var(--church-gray);">{{ viewingPost.content }}</p>
        </div>
        <div class="flex justify-end space-x-2 px-6 py-4 border-t border-gray-100">
          <button @click="startEdit" class="px-4 py-2 text-sm rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 transition">수정</button>
          <button @click="startDelete" class="px-4 py-2 text-sm rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition">삭제</button>
        </div>
      </div>
    </div>

    <!-- 글쓰기 / 수정 폼 모달 -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="closeForm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="text-base font-bold" style="color: var(--church-navy);">{{ editingPost ? '게시글 수정' : '새 글 쓰기' }}</h3>
          <button @click="closeForm" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
          <!-- 작성자 (수정 시 비활성화) -->
          <div v-if="!editingPost" class="grid grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-xs font-semibold" style="color: var(--church-navy);">작성자 *</label>
              <input v-model="form.author" type="text" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="이름을 입력하세요" />
            </div>
            <div class="space-y-1.5">
              <label class="text-xs font-semibold" style="color: var(--church-navy);">비밀번호 * <span class="font-normal text-gray-400">(수정/삭제 시 필요)</span></label>
              <input v-model="form.password" type="password" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="비밀번호 설정" />
            </div>
          </div>
          <div v-else class="space-y-1.5">
            <label class="text-xs font-semibold" style="color: var(--church-navy);">비밀번호 확인 *</label>
            <input v-model="form.password" type="password" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="작성 시 설정한 비밀번호" />
          </div>

          <!-- 제목 -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold" style="color: var(--church-navy);">제목 *</label>
            <input v-model="form.title" type="text" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100" placeholder="제목을 입력하세요" />
          </div>

          <!-- 글 종류 -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold" style="color: var(--church-navy);">글 종류 *</label>
            <select v-model="form.category" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100 bg-white">
              <option value="" disabled>글 종류를 선택하세요</option>
              <option>문의사항</option>
              <option>기능개발요청</option>
              <option>오류신고</option>
              <option>기타</option>
            </select>
          </div>

          <!-- 내용 -->
          <div class="space-y-1.5">
            <label class="text-xs font-semibold" style="color: var(--church-navy);">내용 *</label>
            <textarea v-model="form.content" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-100 min-h-[180px] resize-none" placeholder="내용을 입력하세요"></textarea>
          </div>

          <div v-if="formError" class="text-xs text-red-500 bg-red-50 px-3 py-2 rounded-lg">{{ formError }}</div>
        </div>
        <div class="flex justify-end space-x-2 px-6 py-4 border-t border-gray-100">
          <button @click="closeForm" class="px-4 py-2 text-sm rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition">취소</button>
          <button @click="submitForm" :disabled="isSubmitting" class="px-5 py-2 text-sm font-semibold rounded-lg text-white transition-all hover:opacity-90 disabled:opacity-50" style="background-color: var(--church-navy);">
            {{ isSubmitting ? '처리 중...' : (editingPost ? '수정 완료' : '등록') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div class="text-center mb-5">
          <div class="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </div>
          <h3 class="font-bold text-gray-800">게시글 삭제</h3>
          <p class="text-sm text-gray-500 mt-1">삭제하려면 비밀번호를 입력하세요.</p>
        </div>
        <input v-model="deletePassword" type="password" class="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-red-100 mb-3" placeholder="비밀번호" />
        <div v-if="deleteError" class="text-xs text-red-500 mb-3">{{ deleteError }}</div>
        <div class="flex space-x-2">
          <button @click="showDeleteConfirm = false" class="flex-1 py-2 text-sm rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition">취소</button>
          <button @click="confirmDelete" :disabled="isSubmitting" class="flex-1 py-2 text-sm font-semibold rounded-lg bg-red-500 text-white hover:bg-red-600 transition disabled:opacity-50">
            {{ isSubmitting ? '삭제 중...' : '삭제' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import * as api from '../api'

const posts = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

const viewingPost = ref(null)
const editingPost = ref(null)
const showForm = ref(false)
const showDeleteConfirm = ref(false)
const formError = ref('')
const deleteError = ref('')
const deletePassword = ref('')

const form = reactive({
  author: '',
  title: '',
  category: '',
  content: '',
  password: ''
})

onMounted(loadPosts)

async function loadPosts() {
  isLoading.value = true
  try {
    posts.value = await api.getBoardPosts()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

function openPost(post) {
  viewingPost.value = post
}

function closePost() {
  viewingPost.value = null
  editingPost.value = null
}

function openWriteForm() {
  editingPost.value = null
  form.author = ''
  form.title = ''
  form.category = ''
  form.content = ''
  form.password = ''
  formError.value = ''
  showForm.value = true
}

function startEdit() {
  editingPost.value = viewingPost.value
  form.title = viewingPost.value.title
  form.category = viewingPost.value.category
  form.content = viewingPost.value.content
  form.password = ''
  formError.value = ''
  showForm.value = true
  viewingPost.value = null
}

function startDelete() {
  deletePassword.value = ''
  deleteError.value = ''
  showDeleteConfirm.value = true
}

function closeForm() {
  showForm.value = false
  editingPost.value = null
}

async function submitForm() {
  formError.value = ''
  if (!form.title || !form.category || !form.content || !form.password) {
    formError.value = '모든 필수 항목을 입력해주세요.'
    return
  }
  if (!editingPost.value && !form.author) {
    formError.value = '작성자를 입력해주세요.'
    return
  }

  isSubmitting.value = true
  try {
    if (editingPost.value) {
      const res = await api.updateBoardPost(editingPost.value.row_key, {
        row_key: editingPost.value.row_key,
        password: form.password,
        title: form.title,
        category: form.category,
        content: form.content
      })
      if (!res.success) {
        formError.value = '비밀번호가 올바르지 않습니다.'
        return
      }
    } else {
      await api.createBoardPost({
        author: form.author,
        title: form.title,
        category: form.category,
        content: form.content,
        password: form.password
      })
    }
    closeForm()
    await loadPosts()
  } catch (e) {
    console.error('[게시판 오류] submitForm:', e)
    const status = e.response?.status
    const detail = e.response?.data?.detail
    if (status === 404) {
      formError.value = `[404] 서버에 해당 API가 없습니다. 백엔드가 최신 코드로 실행 중인지 확인하세요.`
    } else if (status === 403) {
      formError.value = '비밀번호가 올바르지 않습니다.'
    } else if (status === 500) {
      formError.value = `[500 서버 오류] ${detail || '서버 내부 오류가 발생했습니다.'}`
    } else if (!e.response) {
      formError.value = '서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인하세요.'
    } else {
      formError.value = `[${status}] ${detail || '알 수 없는 오류가 발생했습니다.'}`
    }
  } finally {
    isSubmitting.value = false
  }
}

async function confirmDelete() {
  deleteError.value = ''
  if (!deletePassword.value) {
    deleteError.value = '비밀번호를 입력하세요.'
    return
  }

  isSubmitting.value = true
  try {
    const res = await api.deleteBoardPost(viewingPost.value.row_key, deletePassword.value)
    if (res.success) {
      showDeleteConfirm.value = false
      closePost()
      await loadPosts()
    }
  } catch (e) {
    deleteError.value = e.response?.data?.detail || '비밀번호가 올바르지 않거나 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

function categoryClass(cat) {
  const map = {
    '문의사항': 'bg-blue-50 text-blue-600',
    '기능개발요청': 'bg-purple-50 text-purple-600',
    '오류신고': 'bg-red-50 text-red-500',
    '기타': 'bg-gray-100 text-gray-500'
  }
  return map[cat] || 'bg-gray-100 text-gray-500'
}
</script>
