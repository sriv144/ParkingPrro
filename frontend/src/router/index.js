import { createRouter, createWebHistory } from "vue-router";

import LandingPage from "@/components/LandingPage.vue";
import LoginPage from "@/components/Login.vue";
import RegisterPage from "@/components/Register.vue";
import AdminLayout from "@/components/AdminDashboard.vue";
import LotList from "@/components/LotList.vue";
import AddLot from "@/components/AddLot.vue";
<<<<<<< HEAD
import EditLot from "@/components/EditParkingLot.vue";
=======
import EditLot from "@/components/EditLot.vue";
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
import OccupiedSpotDetails from "@/components/OccupiedSpotDetails.vue";
import UserList from "@/components/RegisteredUsers.vue";
import SearchParkingLots from "@/components/SearchParkingLots.vue";
import SummaryView from "@/components/SummaryView.vue";

const routes = [
<<<<<<< HEAD
  { path: "/", name: "Home", component: LandingPage },
  { path: "/login", name: "Login", component: LoginPage },
=======
  { path: "/",        name: "Home",      component: LandingPage },
  { path: "/login",   name: "Login",     component: LoginPage   },
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
  { path: "/register", name: "Register", component: RegisterPage },

  {
    path: "/admin",
<<<<<<< HEAD
    component: AdminLayout, // This must include <router-view />
    children: [
      { path: "", name: "AdminDashboard", component: LotList },
      { path: "lots", name: "ParkingLots", component: LotList },
      { path: "add-lot", name: "AddLot", component: AddLot },
      {
        path: "edit-lot/:id",
        name: "EditLot",
        component: EditLot,
        props: true
      },
      {
        path: "occupied-spot/:id",
        name: "OccupiedSpotDetails",
        component: OccupiedSpotDetails,
        props: true
      },
      { path: "users", name: "Users", component: UserList },
      { path: "search", name: "SearchParkingLots", component: SearchParkingLots },
      { path: "summary", name: "Summary", component: SummaryView }
    ]
  },

  // Catch-all route for 404s
=======
    component: AdminLayout,
    children: [
      { path: "",           name: "AdminDashboard",     component: LotList },
      { path: "lots",       name: "ParkingLots",        component: LotList },
      { path: "add-lot",    name: "AddLot",             component: AddLot },
      { path: "edit-lot/:id", name: "EditLot",          component: EditLot, props: true },
      { path: "occupied-spot/:id", name: "OccupiedSpotDetails", component: OccupiedSpotDetails, props: true },
      { path: "users",      name: "Users",              component: UserList },
      { path: "search",     name: "SearchParkingLots",  component: SearchParkingLots },
      { path: "summary",    name: "Summary",            component: SummaryView },
    ]
  },

>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
  { path: "/:pathMatch(.*)*", redirect: "/" }
];

export default createRouter({
  history: createWebHistory(),
<<<<<<< HEAD
  routes
=======
  routes,
>>>>>>> 20f5d19e6e8033dcd30bd885ac124933a0f92348
});
