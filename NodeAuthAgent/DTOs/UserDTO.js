module.exports = class UserDTO
{
    email;
    id;
    username;
    role;

    constructor(model)
    {
        this.role = model.role;
        this.email = model.email;
        this.id = model._id;
        this.username = model.username;   
    }
}