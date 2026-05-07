import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, watch } from "vue";

export const useAuthStore = defineStore("auth", () => {
	const user = ref(null);
	const isLoggedIn = ref(false);
	const ready = ref(false);

	const userResource = createResource({
		url: "zevar_core.api.user_info.get_user_info",
		auto: true,
		onSuccess(data) {
			if (typeof data === "string") {
				if (data === "Guest") {
					user.value = null;
					isLoggedIn.value = false;
				} else {
					user.value = { full_name: data, email: data };
					isLoggedIn.value = true;
				}
			} else {
				user.value = data;
				isLoggedIn.value = true;
			}
			ready.value = true;
		},
		onError(err) {
			console.error("Auth Error:", err);
			user.value = null;
			isLoggedIn.value = false;
			ready.value = true;
		},
	});

	const logoutResource = createResource({
		url: "logout",
		onSuccess() {
			user.value = null;
			isLoggedIn.value = false;
			window.location.reload();
		},
	});

	function logout() {
		logoutResource.submit();
	}

	function init() {
		return new Promise((resolve) => {
			if (ready.value) {
				resolve();
			} else {
				const unwatch = watch(ready, (val) => {
					if (val) {
						unwatch();
						resolve();
					}
				});
			}
		});
	}

	return {
		user,
		isLoggedIn,
		ready,
		userResource,
		logout,
		init,
	};
});
