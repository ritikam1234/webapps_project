"use strict"

function send_alert(message) {
    alert(`${message}`);
}
function getRecipes() {
    $.ajax({
        url: "/homey/get-recipes",
        dataType : "json",
        success: updateRecipes,
        error: updateError
    });
}

function makeEventHTML(event) {
    let eventtitle =``
    if (event.temp_id === -1) {
        console.log("calendar event")
        eventtitle = `<span> ${sanitize(event.title)} </span>`
    }
    else {
        eventtitle = `<a id='id_recipe_title_${event.temp_id}' href='/recipe/${event.temp_id}'> ${sanitize(event.title)}</a>`
    }
    let createdby = `<a> ${sanitize(event.user_first_name)} ${sanitize(event.user_last_name)} </a>`
    let element = `<div class="d-flex justify-content-center" class="text-center mb-4" id='id_event_div_${event.event_id}'> 
            <div class="bg-light p-4 rounded shadow col-md-6" class="col text-center">
            <div class="col text-center" >${createdby} ${event.text} ${eventtitle} at ${new Date(event.time).toLocaleString()}</div>               
            </div>
        </div>
        <br></br>`
    return element
}

function updateEvents(events){
    console.log(events)
    events.forEach(event => {
        if (document.getElementById(`id_event_div_${event.event_id}`) == null) {
            $("#my-events-go-here").prepend(makeEventHTML(event))
        }
    })
}
function getEvents() {
    $.ajax({
        url: "/homey/get-events",
        dataType : "json",
        success: updateEvents,
        error: updateError
    });
    }

function getReviews(recipeid) {
    $.ajax({
        url: `/homey/get-reviews/${recipeid}`,
        dataType : "json",
        success: updateReviews,
        error: updateError
    });
}

function updateError(xhr) {
    if (xhr.status === 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') === 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    $("#error").html(message);
}


function updateRecipes(recipes) {
    console.log(recipes)
    recipes.forEach(recipe => {
        if (document.getElementById(`id_recipe_div_${recipe.id}`) == null) {
            $("#my-recipes-go-here").prepend(makeRecipeHTML(recipe))
        }
    })
}

function updateReviews(reviews) {
    console.log(reviews)
    reviews.forEach(review => {
        if (document.getElementById(`id_review_div_${review.id}`) == null) {
            $("#my-reviews-go-here").prepend(makeReviewHTML(review))
        }
    })
}

function makeRecipeHTML(recipe) {
    let recipelink = `<a id='id_recipe_title_${recipe.id}' href='/recipe/${recipe.id}'> ${sanitize(recipe.title)}</a>`
    let recipepicture = `<div id="recipe_picture_${recipe.id}"> <img id="recipe_picture" src="/recipepicture/${recipe.id}"></img></div>`
    let createdby = `<div> Created by: ${sanitize(recipe.fname)} ${sanitize(recipe.lname)} </div>`
    let rating = `<div> Rating: ${recipe.avg_rating} </div>`
    let tags = `<div id="recipe_tags_${recipe.id}">Tags: ${recipe.tags} </div>`
    let element = `<div class="bg-light p-5 rounded shadow col-md-6" id='id_recipe_div_${recipe.id}'> ${recipelink} ${recipepicture} ${createdby} ${rating} ${tags}</div>`
    return element
}

function makeReviewHTML(review) {
        let reviewedby = `<a id="id_profile_link" href="{% url 'other_profile' ${sanitize(review.user_id)}%}">
             ${sanitize(review.fname)}  ${sanitize(review.lname)}</a> `
        let reviewpicture = `<div id="review_picture_${review.id}"> <img id="review_picture" src="/reviewpicture/${review.id}"></img></div>`
        let rating = `<div> Rating: ${review.rating} </div>`
        let element =`<div id="id_review_div_${review.id}" class="container p-3 bg-body"> Reviewed by: ${reviewedby} ${reviewpicture} ${rating}</div>`
        return element
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}