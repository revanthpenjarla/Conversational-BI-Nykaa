<template>
  <div>
    <CRow>
      <CCol :md="12">
        <CCard class="mb-4 shadow-sm">
          <CCardBody class="text-center p-5">
            <h1 class="display-5 fw-bold text-primary mb-3">Welcome to Nykaa AI Analytics</h1>
            <p class="lead text-muted mb-4">
              Your conversational Business Intelligence dashboard is ready. 
              Talk to your database in plain English.
            </p>
            <CButton color="primary" size="lg" @click="$router.push('/conversational-bi')">
              Launch Ask AI 🧠
            </CButton>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  </div>
</template>

<script setup>
// Clean, empty setup
</script>
