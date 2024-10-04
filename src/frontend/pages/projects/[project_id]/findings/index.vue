<script setup lang="ts">
definePageMeta({ layout: false });
const route = useRoute();
const router = useRouter();
router.push(`/projects/${route.params.project_id}/findings/osint`);
</script>
