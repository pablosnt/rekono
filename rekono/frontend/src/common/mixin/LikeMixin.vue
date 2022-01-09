
<script>
import LikesApi from '@/backend/likes'
export default {
  name: 'likeMixin',
  methods: {
    like (path, id) {
      LikesApi.like(path, id)
    },
    dislike (path, id) {
      LikesApi.dislike(path, id)
    }
  }
}
</script>