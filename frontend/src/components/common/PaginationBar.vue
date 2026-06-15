<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    page: number;
    pageSize: number;
    total: number;
    disabled?: boolean;
  }>(),
  {
    disabled: false,
  },
);

const emit = defineEmits<{
  (event: "change", page: number): void;
}>();

function totalPages(): number {
  return Math.max(1, Math.ceil(props.total / props.pageSize));
}

function changePage(nextPage: number) {
  const target = Math.min(Math.max(1, nextPage), totalPages());
  if (target !== props.page && !props.disabled) {
    emit("change", target);
  }
}
</script>

<template>
  <div class="pagination-bar">
    <span>共 {{ total }} 条</span>
    <div class="pagination-actions">
      <button type="button" :disabled="disabled || page <= 1" @click="changePage(page - 1)">上一页</button>
      <strong>{{ page }} / {{ totalPages() }}</strong>
      <button type="button" :disabled="disabled || page >= totalPages()" @click="changePage(page + 1)">下一页</button>
    </div>
  </div>
</template>
